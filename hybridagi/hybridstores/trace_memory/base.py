"""The base trace memory. Copyright (C) 2023 SynaLinks. License: GPL-3.0"""

from pydantic.v1 import BaseModel
import tiktoken
from collections import deque
from typing import Iterable, Optional, Callable, Any
from langchain.schema.embeddings import Embeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter

from ..hybridstore import BaseHybridStore

TRACE_MEMORY_TEMPLATE = \
"""The Objective is from the perspective of the User
Objective: {objective}
Note: {note}
{actions_trace}"""

class BaseTraceMemory(BaseModel):
    objective: str = "N/A"
    note: str = "N/A"
    actions_trace: Iterable = deque()
    current_program: str = ""
    chunk_size: int = 200

    # def __init__(
    #         self,
    #         index_name: str,
    #         redis_url: str,
    #         embeddings: Embeddings,
    #         embeddings_dim: int,
    #         normalize: Optional[Callable[[Any], Any]] = _default_norm,
    #         verbose: bool = True):
    #     super().__init__(
    #         index_name = index_name,
    #         redis_url = redis_url,
    #         embeddings = embeddings,
    #         embeddings_dim = embeddings_dim,
    #         graph_index = "trace_memory",
    #         indexed_label = "Step",
    #         normalize = normalize,
    #         verbose = verbose,
    #     )

    def clear_trace(self):
        """Method to clear the actions trace"""
        self.actions_trace = deque()

    def get_current_trace(self, max_tokens: int) -> str:
        """Load the memory variables"""
        text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
            chunk_size = self.chunk_size,
            chunk_overlap = 0,
        )
        actions_trace = "\n".join(self.actions_trace)
        texts = text_splitter.split_text(actions_trace)
        result = ""
        if len(texts) == 0:
            memory = TRACE_MEMORY_TEMPLATE.format(
                objective = self.objective,
                note = self.note,
                actions_trace = ""
            )
            return memory
        elif len(texts) == 1:
            memory = TRACE_MEMORY_TEMPLATE.format(
                objective = self.objective,
                note = self.note,
                actions_trace = texts[0]
            )
            return memory
        else:
            result = TRACE_MEMORY_TEMPLATE.format(
                objective = self.objective,
                note = self.note,
                actions_trace = ""
            )
            for i in range(0, len(texts)):
                actions_trace = "\n".join(texts[len(texts)-i:])
                memory = TRACE_MEMORY_TEMPLATE.format(
                    objective = self.objective,
                    note = self.note,
                    actions_trace = actions_trace
                )
                encoding = tiktoken.get_encoding("cl100k_base")
                num_tokens = len(encoding.encode(memory))
                if num_tokens < max_tokens:
                    result = memory
                else:
                    break
            return result

    def get_context(
            self,
            prompt: str,
            max_total_tokens: str,
        ) -> str:
        """Method to get the context given a prompt and max total token"""
        encoding = tiktoken.get_encoding("cl100k_base")
        num_tokens = len(encoding.encode(prompt))
        context = self.get_current_trace(
            max_total_tokens-num_tokens)
        return context

    def update_trace(self, description: str):
        """Method to update the trace"""
        self.actions_trace.append(description)

    def update_objective(self, new_objective: str):
        """Method to update the objective"""
        self.objective = new_objective

    def update_current_program(self, current_program: str):
        """Method to update the current program"""
        self.current_program = current_program

    def update_note(self, new_note: str):
        """Method to update the note"""
        self.note = new_note

    def revert(self, n: int):
        """Method to revert N steps of the actions_trace"""
        for i in range(n):
            self.actions_trace.pop()
            