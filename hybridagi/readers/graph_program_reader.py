from abc import ABC, abstractmethod
from typing import Any
from hybridagi.core.graph_program import GraphProgram

class GraphProgramReader(ABC):

    @abstractmethod
    def read(self, filepath: str) -> GraphProgram:
        pass
    
    def __call__(self, filepath: str) -> GraphProgram:
        return self.read(filepath)