from collections import deque
from typing import Iterable, List, Dict
from pydantic import BaseModel
from langchain.schema import BaseMemory
import tiktoken

class ProgramTraceMemory(BaseMemory, BaseModel):
    memory_key: str = "program_memory"
    objective: str = ""
    program_trace: Iterable = deque()
    max_tokens: int = 4000
    memory_template = \
"""
The Objective is from the perspective of the User
Objective: {objective}
{program_trace}
"""
    def clear(self):
        self.program_trace = deque()

    @property
    def memory_variables(self) -> List[str]:
        """Define the variables we are providing to the prompt."""
        return [self.memory_key]

    def load_memory_variables(self, inputs: Dict[str, Any]) -> Dict[str, str]:
        """Load the memory variables"""
        trace_starting_index = 0
        while True:
            program_trace = "\n".join(self.program_trace[trace_starting_index:])

            memory = memory_template.format(
                objective = self.objective,
                program_trace=program_trace
            )

            encoding = tiktoken.get_encoding("cl100k_base")
            num_tokens = len(encoding.encode(memory))
            if num_tokens > self.max_tokens:
                trace_starting_index += 1
            else:
                self.program_trace = self.program_trace[trace_starting_index:]
                break
        return {self.memory_key: memory}
        
    def update_trace(self, prompt):
        self.program_trace.append(prompt)

    def update_objective(self, objective):
        self.objective = objective
