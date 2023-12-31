"""The program memory. Copyright (C) 2023 SynaLinks. License: GPL-3.0"""

import os
from typing import List, Optional, Callable, Any
from langchain.schema.embeddings import Embeddings
from .base import BaseProgramMemory, _default_norm
from ...utility.tester import TesterUtility

class ProgramMemory(BaseProgramMemory):
    """The Program Memory"""
    def __init__(
            self,
            index_name: str,
            redis_url: str,
            embeddings: Embeddings,
            embeddings_dim: int,
            normalize: Optional[Callable[[Any], Any]] = _default_norm,
            verbose: bool = True):
        """The program memory constructor"""
        super().__init__(
            index_name = index_name,
            redis_url = redis_url,
            embeddings = embeddings,
            embeddings_dim = embeddings_dim,
            normalize = normalize,
            verbose = verbose)
        self.playground = self.create_graph("playground")
        self.program_tester = TesterUtility(program_memory = self)

    def load_folders(
            self,
            folders: List[str]):
        """Method to load a library of programs, no check performed"""
        names = []
        programs = []
        for programs_folder in folders:
            for dirpath, dirnames, filenames in os.walk(programs_folder):
                for filename in filenames:
                    if filename.endswith(".cypher"):
                        program_name = filename.replace(".cypher", "")
                        try:
                            names.append(program_name)
                            source = os.path.join(dirpath, filename)
                            programs.append(open(source, "r").read())
                        except Exception:
                            pass
        self.add_programs(names = names, programs = programs)

    def get_program_names(self):
        """Method to get the program names"""
        program_names = []
        result = self.query("MATCH (n:Program) RETURN n.name AS name")
        for record in result:
            program_names.append(record[0])
        return program_names