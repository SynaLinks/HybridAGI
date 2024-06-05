import os
import abc
from typing import List
from ..hybridstores.fact_memory.fact_memory import FactMemory

class KnowledgeParserBase():

    def __init__(
            self,
            fact_memory: FactMemory,
            valid_extensions: List[str],
        ):
        self.fact_memory = fact_memory
        self.valid_extensions = valid_extensions

    @abc.abstractmethod
    def parse(self, filename: str, content: str):
        pass

    def add_folders(
            self,
            folders: List[str],
        ):
        for i, folder in enumerate(folders):
            folder_name = os.path.basename(folder)
            for dirpath, dirnames, filenames in os.walk(folder):
                for filename in filenames:
                    if not filename.startswith("."):
                        _, extension = os.path.splitext(filename)
                        if extension in self.valid_extensions:
                            source = os.path.join(dirpath, filename)
                            try:
                                f = open(source, "r")
                                file_content = f.read()
                                self.parse(filename, file_content)
                            except Exception:
                                continue
