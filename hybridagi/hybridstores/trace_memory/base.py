"""The base trace memory. Copyright (C) 2023 SynaLinks. License: GPL-3.0"""

from pydantic.v1 import BaseModel
import tiktoken
from collections import deque
from typing import Iterable
from langchain.text_splitter import RecursiveCharacterTextSplitter

TRACE_MEMORY_TEMPLATE = \
"""
### User defined objective

The Objective is from the perspective of the User
Objective: {objective}
Note: {note}

### Past Action

{actions_trace}

### Current Action

Remember that the objective is to {objective}.
Note: {note}
Always reflect to you past actions to known what to do or answer."""

class BaseTraceMemory(BaseModel):
    objective: str = "N/A"
    note: str = "N/A"
    actions_trace: Iterable = deque()
    current_program: str = ""
    chunk_size: int = 200

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
            