## The main program.
## Copyright (C) 2023 SynaLinks.
##
## This program is free software: you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with this program. If not, see <https://www.gnu.org/licenses/>.

import argparse
from colorama import Fore, Style
from langchain.prompts.prompt import PromptTemplate
from langchain.chains.llm import LLMChain
from langchain.embeddings import OpenAIEmbeddings
from langchain.chat_models import ChatOpenAI
from langchain.tools import Tool

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

from hybrid_agi.tools.ask_user import AskUserTool
from hybrid_agi.tools.self_chat import SelfChatTool
from hybrid_agi.tools.upload import Upload2UserTool

from hybrid_agi.agents.planners.htn_planner import HTNPlanner

BANNER =\
"""
o  o o   o o--o  o--o  o-O-o o-o         O   o-o  o-O-o 
|  |  \ /  |   | |   |   |   |  \       / \ o       |   
O--O   O   O--o  O-Oo    |   |   O     o---o|  -o   |   
|  |   |   |   | |  \    |   |  /      |   |o   |   |   
o  o   o   o--o  o   o o-O-o o-o       o   o o-o  o-O-o
    Unleash the Power of Combined Vector and Graph Databases
"""

def main():
    cfg = Config()
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

    virtual_filesystem = VirtualFileSystem(
        hybridstore = hybridstore
    )
    virtual_text_editor = VirtualTextEditor(
        hybridstore = hybridstore,
        llm = llm,
        chunk_size = cfg.chunk_size,
        chunk_overlap = cfg.chunk_overlap,
        verbose = cfg.debug_mode
    )

    if cfg.documentation_directory != "":
        index = VirtualFileSystemIndexWrapper(
            filesystem = virtual_filesystem,
            text_editor = virtual_text_editor
        )
        index.add_folders([cfg.documentation_directory])
    
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

    ask_user = AskUserTool(language=cfg.user_language)
    self_chat = SelfChatTool(llm=llm, language=cfg.language)

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
    
    upload = Upload2UserTool(
        filesystem = virtual_filesystem,
        text_editor = virtual_text_editor,
        downloads_directory=cfg.downloads_directory
    )

    primitives = [
        Tool(
            name=shell_tool.name,
            func=shell_tool.run,
            description=shell_tool.description
        ),
        Tool(
            name=write_file.name,
            func=write_file.run,
            description=write_file.description
        ),
        Tool(
            name=update_file.name,
            func=update_file.run,
            description=write_file.description
        ),
        Tool(
            name=read_file.name,
            func=read_file.run,
            description=write_file.description
        ),
        Tool(
            name=upload.name,
            func=upload.run,
            description=upload.description
        ),
        Tool(
            name=self_chat.name,
            func=self_chat.run,
            description=self_chat.description
        )
    ]

    if cfg.auto_mode is False:
        primitives.extend([
            Tool(
                name=ask_user.name,
                func=ask_user.run,
                description=ask_user.description
            )]
        )
    else:
        print(f"{Fore.YELLOW}[*] WARNING ! Autonomous mode enabled.")

    planner = HTNPlanner(
        hybridstore,
        llm,
        primitives,
        user_language=cfg.user_language,
        user_expertise=cfg.user_expertise,
        max_depth = cfg.max_depth,
        max_breadth = cfg.max_breadth,
        verbose=cfg.debug_mode
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
    print(f"{Fore.YELLOW}[*] {message}{Style.RESET_ALL}")
    objective = input(f"{Fore.YELLOW}> {Style.RESET_ALL}")
    final_result = planner.run(objective)
    print(f"{Fore.YELLOW}[*] {final_result}{Style.RESET_ALL}")
