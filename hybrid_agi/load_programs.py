"""The script to add the programs into the hybridstore. Copyright (C) 2023 SynaLinks. License: GPL-3.0"""

import os
import argparse
from colorama import Fore, Style
from langchain.embeddings import OpenAIEmbeddings
from redisgraph import Graph
from hybrid_agi.config import Config

from hybrid_agi.hybridstores.redisgraph import RedisGraphHybridStore
from hybrid_agi.graph_loaders.cypher_loader import CypherGraphLoader

BANNER =\
f"""{Fore.BLUE}
o  o o   o o--o  o--o  o-O-o o-o         O   o-o  o-O-o 
|  |  \ /  |   | |   |   |   |  \       / \ o       |   
O--O   O   O--o  O-Oo    |   |   O     o---o|  -o   |   
|  |   |   |   | |  \    |   |  /      |   |o   |   |   
o  o   o   o--o  o   o o-O-o o-o       o   o o-o  o-O-o
    {Fore.GREEN}Unleash the Power of Combined Vector and Graph Databases{Style.RESET_ALL}
"""

def main():
    print(BANNER)

    parser = argparse.ArgumentParser(description='Load HybridAGI programs.')
    parser.add_argument('-c', '--clear', action='store_true', help="Clear the hybridstore if enabled")
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

    graph_loader = CypherGraphLoader(client=hybridstore.client)

    print(f"{Fore.GREEN}[*] Adding my program library into the hybridstore... this may take a while.{Style.RESET_ALL}")

    programs_folder = cfg.library_directory
    for dirpath, dirnames, filenames in os.walk(programs_folder):
        for filename in filenames:
            if filename.endswith(".cypher"):
                program_name = filename.replace(".cypher", "")
                program_index = f"{hybridstore.program_key}:{program_name}"
                try:
                    print(f"{Fore.GREEN}[*] Adding '{Fore.YELLOW}{program_name}{Fore.GREEN}' into the hybridstore...{Style.RESET_ALL}")
                    graph_loader.load(os.path.join(dirpath, filename), program_index)
                except Exception as err:
                    print(f"{Fore.RED}[!] Error occured with '{Fore.YELLOW}{filename}{Fore.RED}': {str(err)}{Style.RESET_ALL}")
    print(f"{Fore.GREEN}[*] Done.{Style.RESET_ALL}")

if __name__ == "__main__":
    main()