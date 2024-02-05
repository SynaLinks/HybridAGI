"""The main program. Copyright (C) 2023 SynaLinks. License: GPL-3.0"""

import asyncio
import numpy as np
import os
from colorama import Fore, Style

from langchain.tools import Tool
from langchain_together import Together
from langchain_together.embeddings import TogetherEmbeddings

from hybridagi.config import Config

from hybridagi import FileSystem
from hybridagi import (
    ProgramMemory,
    TraceMemory,
    GraphProgramInterpreter,
)

from hybridagi.toolkits import (
    FileSystemToolKit,
    WebToolKit,
)

from hybridagi.tools import (
    AskUserTool,
    SpeakTool
)

cfg = Config()

def _normalize_vector(value):
    return np.add(np.divide(value, 2), 0.5)

embeddings = TogetherEmbeddings(
        model=cfg.embeddings_model
    )

smart_llm = Together(
    model=cfg.smart_llm_model,
    temperature=cfg.temperature,
    max_tokens=cfg.max_output_tokens,
    top_p=cfg.top_p,
    top_k=cfg.top_k,
    repetition_penalty = cfg.repetition_penalty,
)

fast_llm = Together(
    model = cfg.fast_llm_model,
    temperature = cfg.temperature,
    max_tokens = cfg.max_output_tokens,
    top_p = cfg.top_p,
    top_k = cfg.top_k,
    repetition_penalty = cfg.repetition_penalty,
)

filesystem = FileSystem(
    redis_url = cfg.redis_url,
    index_name = cfg.memory_index,
    embeddings = embeddings,
    embeddings_dim = cfg.embeddings_dim,
    normalize = _normalize_vector)
filesystem.initialize()

program_memory = ProgramMemory(
    redis_url = cfg.redis_url,
    index_name = cfg.memory_index,
    embeddings = embeddings,
    embeddings_dim = cfg.embeddings_dim,
    normalize = _normalize_vector)
program_memory.initialize()

trace_memory = TraceMemory(
    redis_url = cfg.redis_url,
    index_name = cfg.memory_index,
    embeddings = embeddings,
    embeddings_dim = cfg.embeddings_dim,
    normalize = _normalize_vector)
trace_memory.initialize()

ask_user = AskUserTool()
speak = SpeakTool()

tools = [
    Tool(
        name=ask_user.name,
        func=ask_user.run,
        description=ask_user.description),
    Tool(
        name=speak.name,
        func=speak.run,
        description=speak.description),
]

toolkits = [
    FileSystemToolKit(
        filesystem = filesystem,
        downloads_directory = cfg.downloads_directory,
    ),
    WebToolKit(
        filesystem = filesystem,
        user_agent = cfg.user_agent,
    )
]

interpreter = GraphProgramInterpreter(
    program_memory = program_memory,
    trace_memory = trace_memory,
    smart_llm = smart_llm,
    fast_llm = fast_llm,
    tools = tools,
    toolkits = toolkits,
    smart_llm_max_token = cfg.smart_llm_max_token,
    fast_llm_max_token = cfg.fast_llm_max_token,
    max_decision_attemps = cfg.max_decision_attemps,
    max_evaluation_attemps = cfg.max_evaluation_attemps,
    max_iteration = cfg.max_iteration,
    verbose = cfg.verbose,
    debug = cfg.debug_mode
)

BANNER = \
f"""{Fore.BLUE}
o  o o   o o--o  o--o  o-O-o o-o         O   o-o  o-O-o 
|  |  \ /  |   | |   |   |   |  \       / \ o       |   
O--O   O   O--o  O-Oo    |   |   O     o---o|  -o   |   
|  |   |   |   | |  \    |   |  /      |   |o   |   |   
o  o   o   o--o  o   o o-O-o o-o       o   o o-o  o-O-o
    {Fore.GREEN}The Programmable Neuro-Symbolic AGI{Style.RESET_ALL}
"""

MENU = \
f"""{Fore.YELLOW}[*] Please choose one of the following option:

1 - Clean the hybrid vector/graph database
2 - Load the library of Cypher programs
3 - Load a folder into the hybrid database
4 - Start HybridAGI (programs must have been loaded){Style.RESET_ALL}"""

async def main():
    print(BANNER)
    while True:
        print(MENU)
        while True:
            try:
                choice = int(input("> "))
                if choice < 5 and choice > 0:
                    break
            except ValueError:
                pass
        if choice == 1:
            clean_database()
        elif choice == 2:
            load_programs()
        elif choice == 3:
            load_folder()
        elif choice == 4:
            await run_agent()

def clean_database():
    print(f"{Fore.GREEN}[*] Cleaning the hybrid database...{Style.RESET_ALL}")
    filesystem.clear()
    filesystem.initialize()
    program_memory.initialize()
    print(f"{Fore.GREEN}[*] Done.{Style.RESET_ALL}")

def load_folder():
    print(f"{Fore.GREEN}[*] Which folder do you want to load?{Style.RESET_ALL}")
    folder_path = input("> ")
    folder_name = os.path.basename(os.path.abspath(folder_path))
    print(
        f"{Fore.GREEN}[*] Are you sure about loading the folder named " \
        + f"'{folder_name}'? [y/N]{Style.RESET_ALL}")
    while True:
        decision = input("> ").upper().strip()
        if decision == "Y" or decision == "YES":
            break
        elif decision == "N" or decision == "NO":
            return
    print(
        f"{Fore.GREEN}[*] Adding '{folder_name}' folder into the hybridstore..."+
        f"this may take a while.{Style.RESET_ALL}"
    )
    try:
        filesystem.add_folders(
            [folder_path],
            folder_names=[f"/home/user/{folder_name}"])
    except Exception as err:
        print(f"{Fore.RED}[!] Error occured: {err}{Style.RESET_ALL}")

def load_programs():
    print(f"{Fore.GREEN}[*] Loading programs...")
    print(f"[*] This may take a while.{Style.RESET_ALL}")
    program_memory.load_folders([cfg.library_directory])
    print(f"{Fore.GREEN}[*] Done.{Style.RESET_ALL}")

async def run_agent():
    message = "Please, write your objective then press [Enter]"
    print(f"{Fore.GREEN}[*] {message}{Style.RESET_ALL}")
    objective = input("> ")
    try:
        result = await interpreter.async_run(objective)
        print(f"{Fore.YELLOW}[*] {result}{Style.RESET_ALL}")
    except Exception as err:
        print(f"{Fore.RED}[!] Error occured: {err}{Style.RESET_ALL}")

if __name__ == "__main__":
    asyncio.run(main())