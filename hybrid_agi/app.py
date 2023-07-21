"""The main app. Copyright (C) 2023 SynaLinks. License: GPL-3.0"""

from langchain.prompts.prompt import PromptTemplate
from langchain.chains.llm import LLMChain
from langchain.embeddings import OpenAIEmbeddings
from langchain.chat_models import ChatOpenAI
from langchain.tools import Tool

import chainlit as cl

from hybrid_agi.config import Config

from hybrid_agi.hybridstores.redisgraph import RedisGraphHybridStore
from hybrid_agi.filesystem.filesystem import VirtualFileSystem
from hybrid_agi.filesystem.shell import VirtualShell
from hybrid_agi.filesystem.text_editor import VirtualTextEditor
from hybrid_agi.indexes.filesystem import VirtualFileSystemIndexWrapper

from hybrid_agi.filesystem.commands import (
    ChangeDirectory,
    ListDirectory,
    MakeDirectory,
    Move,
    PrintWorkingDirectory,
    Remove
)

from hybrid_agi.tools.virtual_shell import VirtualShellTool

from hybrid_agi.tools.text_editor import (
    WriteFileTool,
    UpdateFileTool,
    ReadFileTool
)

from hybrid_agi.tools.ui.ask_user import UIAskUserTool
from hybrid_agi.tools.ui.speak import UISpeakTool
from hybrid_agi.tools.ui.upload import UIUploadTool

from hybrid_agi.agents.interpreters.program_interpreter import GraphProgramInterpreter

from hybrid_agi.prompt import HYBRID_AGI_SELF_DESCRIPTION

cfg = Config()

@cl.on_chat_start
def start():
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
    template = """
    You are Hybrid AGI, please greet the user in {language}.
    At the end, ask about what they want to do.
    Output:"""
    prompt = PromptTemplate(
        input_variables=["language"],
        template = template
    )
    message = LLMChain(llm=llm, prompt=prompt).predict(
        language = cfg.user_language
    )
    cl.Message(
        content = message
    ).send()

@cl.langchain_factory
def load():
    embedding = OpenAIEmbeddings()

    llm = None
    if cfg.private_mode is True:
        llm = ChatOpenAI(temperature=cfg.temperature, model_name=cfg.fast_llm_model, openai_api_base=cfg.openai_base_path)
    else:
        llm = ChatOpenAI(temperature=cfg.temperature, model_name=cfg.fast_llm_model)

    hybridstore = RedisGraphHybridStore(
        redis_url = cfg.redis_url,
        index_name = cfg.memory_index,
        embedding_function = embedding.embed_query
    )

    if cfg.wipe_redis_on_start:
        hybridstore.clear()

    virtual_filesystem = VirtualFileSystem(hybridstore)

    virtual_text_editor = VirtualTextEditor(
        hybridstore = hybridstore,
        llm = llm,
        chunk_size = cfg.chunk_size,
        chunk_overlap = cfg.chunk_overlap,
        verbose = cfg.debug_mode
    )

    if cfg.wipe_redis_on_start:
        index = VirtualFileSystemIndexWrapper(
            hybridstore = hybridstore,
            filesystem = virtual_filesystem,
            text_editor = virtual_text_editor
        )
        index.add_folders(["../HybridAGI"], folder_names=["/home/user/HybridAGI"])

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

    ask_user = UIAskUserTool()
    speak = UISpeakTool()

    shell_tool = VirtualShellTool(virtual_shell=virtual_shell)

    write_file = WriteFileTool(
        filesystem=virtual_filesystem,
        text_editor=virtual_text_editor
    )

    update_file = UpdateFileTool(
        filesystem=virtual_filesystem,
        text_editor=virtual_text_editor
    )

    read_file = ReadFileTool(
        filesystem=virtual_filesystem,
        text_editor=virtual_text_editor
    )
    
    upload = UIUploadTool(
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
            name=update_file.name,
            func=update_file.run,
            description=update_file.description
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

    instructions = HYBRID_AGI_SELF_DESCRIPTION

    interpreter = GraphProgramInterpreter(
        hybridstore,
        llm,
        prompt = instructions,
        tools = tools,
        language = cfg.user_language,
        max_iteration = cfg.max_iteration,
        monitoring = cfg.monitoring,
        verbose = cfg.debug_mode
    )
    return interpreter

@cl.langchain_run
def run(agent, input):
    res = agent.run(input)
    cl.Message(content=res).send()