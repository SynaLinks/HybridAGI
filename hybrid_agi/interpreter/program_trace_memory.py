"""The program trace memory. Copyright (C) 2023 SynaLinks. License: GPL-3.0"""

from collections import deque
from typing import Iterable, List, Dict, Any
from pydantic import BaseModel
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
        trace_starting_index = 0
        while True:
            if trace_starting_index > 0:
                print(trace_starting_index)
                program_trace = "\n".join(self.program_trace[trace_starting_index:])
            else:
                program_trace = "\n".join(self.program_trace)

            memory = self.memory_template.format(
                objective = self.objective,
                program_trace=program_trace
            )

            encoding = tiktoken.get_encoding("cl100k_base")
            num_tokens = len(encoding.encode(memory))
            if num_tokens > max_tokens:
                trace_starting_index += 1
            else:
                if trace_starting_index > 0:
                    self.program_trace = self.program_trace[trace_starting_index:]
                break
        return memory

    def update_trace(self, prompt):
        self.program_trace.append(prompt)

    def update_objective(self, objective):
        self.objective = objective
