"""The source loader. Copyright (C) 2023 SynaLinks. License: GPL-3.0"""

import argparse
from colorama import Fore, Style
from langchain.embeddings import OpenAIEmbeddings

from hybrid_agi.config import Config

from symbolinks import (
    RedisGraphHybridStore,
    VirtualFileSystem,
    VirtualTextEditor,
    VirtualFileSystemIndexWrapper
)

from hybrid_agi.banner import BANNER

def main():
    print(BANNER)

    parser = argparse.ArgumentParser(description='Load HybridAGI source code.')
    parser.add_argument(
        '-c',
        '--clear',
        action='store_true',
        help="Clear the hybridstore if enabled"
    )
    args = parser.parse_args()

    cfg = Config()

    embedding = OpenAIEmbeddings()

    hybridstore = RedisGraphHybridStore(
        redis_url = cfg.redis_url,
        index_name = cfg.memory_index,
        embedding_function = embedding.embed_query
    )

    if args.clear:
        hybridstore.clear()

    virtual_filesystem = VirtualFileSystem(hybridstore)

    virtual_text_editor = VirtualTextEditor(
        hybridstore = hybridstore,
        chunk_size = cfg.chunk_size,
        chunk_overlap = cfg.chunk_overlap,
        verbose = cfg.debug_mode
    )

    print(
        f"{Fore.GREEN}[*] Adding my own source code into the hybridstore..." +
        f" this may take a while.{Style.RESET_ALL}"
    )
    index = VirtualFileSystemIndexWrapper(
        hybridstore = hybridstore,
        filesystem = virtual_filesystem,
        text_editor = virtual_text_editor,
        verbose = cfg.debug_mode
    )
    index.add_folders(
        ["../HybridAGI", cfg.library_directory],
        folder_names=[
            "/home/user/Workspace/HybridAGI",
            "/home/user/Workspace/MyGraphPrograms"
        ]
    )
    print(f"{Fore.YELLOW}[*] Done.{Style.RESET_ALL}")

if __name__ == "__main__":
    main()