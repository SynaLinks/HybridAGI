"""The program trace memory. Copyright (C) 2023 SynaLinks. License: GPL-3.0"""

from collections import deque
from typing import Iterable, List, Dict, Any
from pydantic import BaseModel
from langchain.text_splitter import RecursiveCharacterTextSplitter
import tiktoken

class ProgramTraceMemory(BaseModel):
    objective: str = ""
    program_trace: Iterable = deque()
    memory_template = \
"""
The Objective is from the perspective of the User
Objective: {objective}
{program_trace}
"""
    def clear(self):
        self.program_trace = deque()

    def get_trace(self, max_tokens: int) -> str:
        """Load the memory variables"""
        text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
            chunk_size=100, chunk_overlap=0
        )
        program_trace = "\n".join(self.program_trace)
        texts = text_splitter.split_text(program_trace)
        result = ""
        for i in range(0, len(texts)):
            program_trace = "\n".join(texts[len(texts)-i:])

            memory = self.memory_template.format(
                objective = self.objective,
                program_trace=program_trace
            )

            encoding = tiktoken.get_encoding("cl100k_base")
            num_tokens = len(encoding.encode(memory))
            if num_tokens < max_tokens:
                result = memory
            else:
                break
        return result

    def update_trace(self, prompt):
        self.program_trace.append(prompt)

    def update_objective(self, objective):
        self.objective = objective
