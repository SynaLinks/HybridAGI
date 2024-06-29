import os
from typing import List
from ..hybridstores.program_memory.program_memory import ProgramMemory


class GraphProgramsLoader():

    def __init__(
            self,
            program_memory: ProgramMemory,
        ):
        """Constructor"""
        self.program_memory = program_memory

    def from_folders(
            self,
            folders: List[str],
        ):
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
        return self.program_memory.add_texts(texts = programs, ids = names)