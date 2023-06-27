"""The script to add the main program into the hybridstore. Copyright (C) 2023 SynaLinks. License: GPLv3"""

from colorama import Fore, Style
from langchain.embeddings import OpenAIEmbeddings

from hybrid_agi.config import Config

from hybrid_agi.hybridstores.redisgraph import RedisGraphHybridStore
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

    hybridstore = RedisGraphHybridStore(
        redis_url = cfg.redis_url,
        index_name = cfg.memory_index,
        embedding_function = embedding.embed_query
    )
    try:
        hybridstore.main.delete()
    except:
        pass

    print(f"{Fore.YELLOW}[*] Loading my main program into the hybridstore...{Style.RESET_ALL}")
    graph_loader = CypherGraphLoader(client=hybridstore.client)
    graph_loader.load("main.cypher", f"{hybridstore.main.name}")
    print(f"{Fore.YELLOW}[*] Done.{Style.RESET_ALL}")