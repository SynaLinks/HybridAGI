import os
from abc import ABC, abstractmethod
from typing import Any
from hybridagi.core.graph_program import GraphProgram

class GraphProgramReader():

    def read(self, filepath: str) -> GraphProgram:
        if not filepath.endswith(".cypher"):
            raise ValueError("GraphProgramReader can only read .cypher programs")
        name = os.path.basename(filepath).replace(".cypher", "")
        result = GraphProgram(name=name)
        if not filepath.endswith(".cypher"):
            raise ValueError("GraphProgramReader can only read .cypher programs")
        with open(filepath, "r") as f:
            graph_program = f.read()
        result.from_cypher(graph_program)
        result.build()
        return result
    
    def __call__(self, filepath: str) -> GraphProgram:
        return self.read(filepath)