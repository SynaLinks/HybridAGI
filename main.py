"""The main program. Copyright (C) 2023 SynaLinks. License: GPL-3.0"""

import os
from colorama import Fore, Style

from langchain.tools import Tool

from config import Config

from hybridagikb import FileSystem

from hybridagikb.tools import (
    ShellTool,
    WriteFilesTool,
    AppendFilesTool,
    ReadFileTool,
    UploadTool)

from hybridagi import ProgramMemory

from hybridagi.tools import (
    AskUserTool,
    SpeakTool,
    ListProgramsTool,
    LoadProgramsTool,
    ProgramSearchTool)

from hybridagi.tools.ask_user import AskUserTool
from hybridagi.tools.speak import SpeakTool

from hybridagi import GraphProgramInterpreter

cfg = Config()

if cfg.private_mode:
    from langchain.embeddings import GPT4AllEmbeddings
    from langchain.llms import GPT4All
    from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
    
    embedding = GPT4AllEmbeddings()
    embedding_dim = 384

    local_path = cfg.local_model_path
    callbacks = [StreamingStdOutCallbackHandler()]

    smart_llm = GPT4All(
        model = local_path,
        temperature=cfg.temperature,
        model_name=cfg.fast_llm_model,
        openai_api_base=cfg.openai_base_path
    )
    fast_llm = GPT4All(
        model = local_path,
        temperature=cfg.temperature,
        model_name=cfg.fast_llm_model,
        openai_api_base=cfg.openai_base_path)
else:
    from langchain.embeddings import OpenAIEmbeddings
    from langchain.chat_models import ChatOpenAI
    
    embedding = OpenAIEmbeddings()
    embedding_dim = 1536
    
    smart_llm = ChatOpenAI(
        temperature=cfg.temperature,
        model_name=cfg.smart_llm_model)
    fast_llm = ChatOpenAI(
        temperature=cfg.temperature,
        model_name=cfg.fast_llm_model)

filesystem = FileSystem(
    redis_url = cfg.redis_url,
    index_name = cfg.memory_index,
    embedding = embedding,
    embedding_dim = embedding_dim)
filesystem.initialize()

program_memory = ProgramMemory(
    redis_url = cfg.redis_url,
    index_name = cfg.memory_index,
    embedding = embedding,
    embedding_dim = embedding_dim,
    llm = fast_llm)
program_memory.initialize()

ask_user = AskUserTool()
speak = SpeakTool()

list_programs = ListProgramsTool(program_memory=program_memory)
load_programs = LoadProgramsTool(program_memory=program_memory)
program_search = ProgramSearchTool(program_memory=program_memory)

shell_tool = ShellTool(filesystem=filesystem)
write_files = WriteFilesTool(filesystem=filesystem)
append_files = AppendFilesTool(filesystem=filesystem)
read_file = ReadFileTool(filesystem=filesystem)
upload = UploadTool(
    filesystem = filesystem,
    downloads_directory = cfg.downloads_directory)

tools = [
    Tool(
        name=ask_user.name,
        func=ask_user.run,
        description=ask_user.description),
    Tool(
        name=speak.name,
        func=speak.run,
        description=speak.description),
    Tool(
        name=write_files.name,
        func=write_files.run,
        description=write_files.description),
    Tool(
        name=append_files.name,
        func=append_files.run,
        description=append_files.description),
    Tool(
        name=read_file.name,
        func=read_file.run,
        description=read_file.description),
    Tool(
        name=upload.name,
        func=upload.run,
        description=upload.description),
    Tool(
        name=shell_tool.name,
        func=shell_tool.run,
        description=shell_tool.description),
    Tool(
        name=list_programs.name,
        func=list_programs.run,
        description=list_programs.description),
    Tool(
        name=load_programs.name,
        func=load_programs.run,
        description=load_programs.description),
    Tool(
        name=program_search.name,
        func=program_search.run,
        description=program_search.description)
]

interpreter = GraphProgramInterpreter(
    program_memory = program_memory,
    smart_llm = smart_llm,
    fast_llm = fast_llm,
    tools = tools,
    smart_llm_max_token = cfg.smart_llm_max_token,
    fast_llm_max_token = cfg.fast_llm_max_token,
    max_decision_attemp = cfg.max_decision_attemp,
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

def main():
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
            run_agent()

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
        + "'{folder_name}'? [y/N]{Style.RESET_ALL}"
    )
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
            folder_names=[f"/home/user/Workspace/{folder_name}"]
        )
    except Exception as err:
        print(f"{Fore.RED}[!] Error occured: {err}{Style.RESET_ALL}")

def load_programs():
    print(f"{Fore.GREEN}[*] Loading programs... This may take a while.{Style.RESET_ALL}")
    program_memory.load_folders([cfg.library_directory])
    print(f"{Fore.GREEN}[*] Done.{Style.RESET_ALL}")

def run_agent():
    message = "Please, write your objective then press [Enter]"
    print(f"{Fore.GREEN}[*] {message}{Style.RESET_ALL}")
    objective = input("> ")
    try:
        result = interpreter.run(objective)
        print(f"{Fore.YELLOW}[*] {result}{Style.RESET_ALL}")
    except Exception as err:
        print(f"{Fore.RED}[!] Error occured: {err}{Style.RESET_ALL}")

if __name__ == "__main__":
    main()