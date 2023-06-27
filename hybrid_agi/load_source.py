"""The script to add HybridAGI source code into the hybridstore. Copyright (C) 2023 SynaLinks. License: GPLv3"""

import argparse
from colorama import Fore, Style
from langchain.embeddings import OpenAIEmbeddings
from langchain.chat_models import ChatOpenAI

from hybrid_agi.config import Config

from hybrid_agi.hybridstores.redisgraph import RedisGraphHybridStore
from hybrid_agi.filesystem.filesystem import VirtualFileSystem

from hybrid_agi.filesystem.text_editor import VirtualTextEditor
from hybrid_agi.indexes.filesystem import VirtualFileSystemIndexWrapper
from hybrid_agi.graph_loaders.cypher_loader import CypherGraphLoader

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
    print(f"{Fore.YELLOW}{BANNER}{Style.RESET_ALL}")
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

    hybridstore.clear()

    virtual_filesystem = VirtualFileSystem(hybridstore)

    virtual_text_editor = VirtualTextEditor(
        hybridstore = hybridstore,
        llm = llm,
        chunk_size = cfg.chunk_size,
        chunk_overlap = cfg.chunk_overlap,
        verbose = cfg.debug_mode
    )

    print(f"{Fore.YELLOW}[*] Adding my own source code into the hybridstore... this may take a while.{Style.RESET_ALL}")
    index = VirtualFileSystemIndexWrapper(
        hybridstore = hybridstore,
        filesystem = virtual_filesystem,
        text_editor = virtual_text_editor,
        verbose = cfg.debug_mode
    )
    index.add_folders(["../HybridAGI"], folder_names=["/home/user/Workspace/HybridAGI"])
    print(f"{Fore.YELLOW}[*] Done.{Style.RESET_ALL}")

if __name__ == "__main__":
    main()