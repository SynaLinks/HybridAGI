"""The main program. Copyright (C) 2023 SynaLinks. License: GPL-3.0"""


import asyncio
import numpy as np
from colorama import Fore, Style
from typing import List

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

from fastapi import FastAPI

app = FastAPI()

cfg = Config()

def _normalize_vector(value):
    return np.add(np.divide(value, 2), 0.5)

embeddings = TogetherEmbeddings(model=cfg.embeddings_model)
embeddings_dim = 768

smart_llm = Together(
    model=cfg.smart_llm_model,
    temperature=cfg.temperature,
    max_tokens=cfg.max_output_tokens,
    top_p=cfg.top_p,
    top_k=cfg.top_k,
)
fast_llm = Together(
    model=cfg.fast_llm_model,
    temperature=cfg.temperature,
    max_tokens=cfg.max_output_tokens,
    top_p=cfg.top_p,
    top_k=cfg.top_k,
)

filesystem = FileSystem(
    redis_url = cfg.redis_url,
    index_name = cfg.memory_index,
    embeddings = embeddings,
    embeddings_dim = embeddings_dim,
    normalize = _normalize_vector)
filesystem.initialize()

program_memory = ProgramMemory(
    redis_url = cfg.redis_url,
    index_name = cfg.memory_index,
    embeddings = embeddings,
    embeddings_dim = embeddings_dim,
    normalize = _normalize_vector)
program_memory.initialize()

trace_memory = TraceMemory(
    redis_url = cfg.redis_url,
    index_name = cfg.memory_index,
    embeddings = embeddings,
    embeddings_dim = embeddings_dim,
    normalize = _normalize_vector)
trace_memory.initialize()

tools = []

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

@app.post("/clean_database")
def clean_database():
    print(f"{Fore.GREEN}[*] Cleaning the hybrid database...{Style.RESET_ALL}")
    filesystem.clear()
    filesystem.initialize()
    program_memory.initialize()
    print(f"{Fore.GREEN}[*] Done.{Style.RESET_ALL}")

@app.post("/load_programs")
def load_programs(names: List[str], programs: List[str]):
    try:
        program_memory.add_programs(names = names, programs = programs)
        return "Success"
    except Exception as err:
        return str(err)

@app.post("/run")
def run_interperter(objective: str):
    try:
        result = asyncio.run(interpreter.async_run(objective))
        print(f"{Fore.YELLOW}[*] {result}{Style.RESET_ALL}")
    except Exception as err:
        print(f"{Fore.RED}[!] Error occured: {err}{Style.RESET_ALL}")