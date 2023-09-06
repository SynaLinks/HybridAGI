"""The main program. Copyright (C) 2023 SynaLinks. License: GPL-3.0"""
import redis
from colorama import Fore, Style
from langchain.prompts.prompt import PromptTemplate
from langchain.chains.llm import LLMChain
from langchain.embeddings import OpenAIEmbeddings
from langchain.chat_models import ChatOpenAI
from langchain.tools import Tool

from hybrid_agi.config import Config

from symbolinks import (
    RedisGraphHybridStore,
    VirtualFileSystem,
    VirtualShell,
    VirtualTextEditor,
    VirtualFileSystemIndexWrapper
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
    ReadFileTool,
    UploadTool
)

from hybrid_agi.tools.ask_user import AskUserTool
from hybrid_agi.tools.speak import SpeakTool

from hybrid_agi.interpreter.graph_program_interpreter import GraphProgramInterpreter

from hybrid_agi.prompt import HYBRID_AGI_BOARD_TEMPLATE

cfg = Config()

from hybrid_agi.banner import BANNER

def main():
    print(BANNER)
    try:
        r = redis.Redis()
        r.ping()
    except:
        print(f"{Fore.RED}[!] Please make sure that Redis is up and running before starting.{Style.RESET_ALL}")
    llm = None
    if cfg.private_mode is True:
        llm = ChatOpenAI(
            temperature=cfg.temperature,
            model_name=cfg.fast_llm_model,
            openai_api_base=cfg.openai_base_path
        )
    else:
        llm = ChatOpenAI(
            temperature=cfg.temperature,
            model_name=cfg.fast_llm_model
        )
    
    message = "Please, write your objective then press [Enter]"
    print(f"{Fore.GREEN}[*] {message}{Style.RESET_ALL}")
    objective = input("> ")

    embedding = OpenAIEmbeddings()

    hybridstore = RedisGraphHybridStore(
        redis_url = cfg.redis_url,
        index_name = cfg.memory_index,
        embedding_function = embedding.embed_query
    )
    
    virtual_filesystem = VirtualFileSystem(hybridstore)

    virtual_text_editor = VirtualTextEditor(
        hybridstore = hybridstore,
        chunk_size = cfg.chunk_size,
        chunk_overlap = cfg.chunk_overlap,
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

    read_file = ReadFileTool(
        filesystem=virtual_filesystem,
        text_editor=virtual_text_editor
    )
    
    upload = UploadTool(
        hybridstore = hybridstore,
        filesystem = virtual_filesystem,
        text_editor = virtual_text_editor,
        downloads_directory = cfg.downloads_directory
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
        hybridstore,
        llm,
        prompt = HYBRID_AGI_BOARD_TEMPLATE,
        tools = tools,
        max_iterations = cfg.max_iterations,
        monitoring = cfg.monitoring,
        verbose = cfg.verbose,
        debug = cfg.debug_mode
    )
    result = interpreter.run(objective)
    print(f"{Fore.YELLOW}[*] {result}{Style.RESET_ALL}")

if __name__ == "__main__":
    main()