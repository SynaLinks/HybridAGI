"""The main program. Copyright (C) 2023 SynaLinks. License: GPL-3.0"""

import os
from colorama import Fore, Style
from langchain.embeddings import OpenAIEmbeddings
from langchain.chat_models import ChatOpenAI
from langchain.tools import Tool

from config import Config

from symbolinks import (
    RedisGraphHybridStore,
    VirtualFileSystem,
    VirtualShell,
    VirtualTextEditor,
    VirtualFileSystemIndexWrapper,
    CypherGraphLoader
)

from symbolinks.filesystem.commands import (
    ChangeDirectory,
    ListDirectory,
    MakeDirectory,
    Move,
    PrintWorkingDirectory,
    Remove
)

from symbolinks.tools import (
    VirtualShellTool,
    WriteFileTool,
    AppendFileTool,
    ReadFileTool,
    UploadTool
)

from hybrid_agi.tools.ask_user import AskUserTool
from hybrid_agi.tools.speak import SpeakTool

from hybrid_agi.interpreter.graph_program_interpreter import GraphProgramInterpreter

cfg = Config()

if cfg.private_mode is True:
    smart_llm = ChatOpenAI(
        temperature=cfg.temperature,
        model_name=cfg.fast_llm_model,
        openai_api_base=cfg.openai_base_path
    )
    fast_llm = ChatOpenAI(
        temperature=cfg.temperature,
        model_name=cfg.fast_llm_model,
        openai_api_base=cfg.openai_base_path
    )
else:
    smart_llm = ChatOpenAI(
        temperature=cfg.temperature,
        model_name=cfg.smart_llm_model
    )
    fast_llm = ChatOpenAI(
        temperature=cfg.temperature,
        model_name=cfg.fast_llm_model
    )

embedding = OpenAIEmbeddings()

hybridstore = RedisGraphHybridStore(
    redis_url = cfg.redis_url,
    index_name = cfg.memory_index,
    embedding = embedding
)

virtual_filesystem = VirtualFileSystem(hybridstore)

virtual_text_editor = VirtualTextEditor(
    hybridstore = hybridstore,
    downloads_directory = cfg.downloads_directory,
    chunk_size = cfg.chunk_size,
    chunk_overlap = cfg.chunk_overlap,
    verbose = cfg.debug_mode
)

index = VirtualFileSystemIndexWrapper(
    hybridstore = hybridstore,
    filesystem = virtual_filesystem,
    text_editor = virtual_text_editor,
    verbose = cfg.debug_mode
)

commands = [
    ChangeDirectory(hybridstore=hybridstore),
    ListDirectory(hybridstore=hybridstore),
    MakeDirectory(hybridstore=hybridstore),
    Move(hybridstore=hybridstore),
    PrintWorkingDirectory(hybridstore=hybridstore),
    Remove(hybridstore=hybridstore)
]

virtual_shell = VirtualShell(
    hybridstore = hybridstore,
    filesystem = virtual_filesystem,
    commands = commands
)

ask_user = AskUserTool()
speak = SpeakTool()

shell_tool = VirtualShellTool(virtual_shell=virtual_shell)

write_file = WriteFileTool(
    filesystem=virtual_filesystem,
    text_editor=virtual_text_editor
)

append_file = AppendFileTool(
    filesystem=virtual_filesystem,
    text_editor=virtual_text_editor
)

read_file = ReadFileTool(
    filesystem=virtual_filesystem,
    text_editor=virtual_text_editor
)

upload = UploadTool(
    hybridstore = hybridstore,
    filesystem = virtual_filesystem,
    text_editor = virtual_text_editor
)

tools = [
    Tool(
        name=ask_user.name,
        func=ask_user.run,
        description=ask_user.description
    ),
    Tool(
        name=speak.name,
        func=speak.run,
        description=speak.description
    ),
    Tool(
        name=write_file.name,
        func=write_file.run,
        description=write_file.description
    ),
    Tool(
        name=append_file.name,
        func=append_file.run,
        description=append_file.description
    ),
    Tool(
        name=read_file.name,
        func=read_file.run,
        description=read_file.description
    ),
    Tool(
        name=upload.name,
        func=upload.run,
        description=upload.description
    ),
    Tool(
        name=shell_tool.name,
        func=shell_tool.run,
        description=shell_tool.description
    )
]

interpreter = GraphProgramInterpreter(
    hybridstore = hybridstore,
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
    {Fore.GREEN}Unleash the Power of Neuro-Symbolic AGI{Style.RESET_ALL}
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
    hybridstore.clear()
    virtual_filesystem.initialize()
    print(f"{Fore.GREEN}[*] Done.{Style.RESET_ALL}")

def load_folder():
    print(f"{Fore.GREEN}[*] Which folder do you want to load?{Style.RESET_ALL}")
    folder_path = input("> ")
    folder_name = os.path.basename(os.path.abspath(folder_path))
    print(f"{Fore.GREEN}[*] Are you sure you want to load the folder named '{folder_name}'? [y/N]{Style.RESET_ALL}")
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
        index.add_folders(
            [folder_path],
            folder_names=[f"/home/user/Workspace/{folder_name}"]
        )
    except Exception as err:
        print(f"{Fore.RED}[!] Error occured: {err}{Style.RESET_ALL}")

def load_programs():
    graph_loader = CypherGraphLoader(client=hybridstore.client)
    print(
        f"{Fore.GREEN}[*] Loading programs at '{cfg.library_directory}'... " +
        f"this may take a while.{Style.RESET_ALL}"
    )
    programs_folder = cfg.library_directory
    for dirpath, dirnames, filenames in os.walk(programs_folder):
        for filename in filenames:
            if filename.endswith(".cypher"):
                program_name = filename.replace(".cypher", "")
                program_index = f"{hybridstore.program_key}:{program_name}"
                try:
                    print(
                        f"{Fore.GREEN}[*] Adding program '{Fore.YELLOW}{program_name}"+
                        f"{Fore.GREEN}'...{Style.RESET_ALL}"
                    )
                    graph_loader.load(os.path.join(dirpath, filename), program_index, clear=True)
                except Exception as err:
                    print(f"{Fore.RED}[!] Error occured with '{Fore.YELLOW}{filename}"+
                        f"{Fore.RED}': {str(err)}{Style.RESET_ALL}"
                    )
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