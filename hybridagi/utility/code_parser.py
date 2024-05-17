import os
from collections import deque
from ..hybridstores.fact_memory.fact_memory import FactMemory
from typing import List

from .knowledge_parsers.python import PythonKnowledgeParser

class CodeParserUtility():

    def __init__(
            self,
            fact_memory: FactMemory,
            language: str,
        ):
        self.fact_memory = fact_memory
        if language == "python":
            self.language = language
            self.extension = ".py"
            self.parser = PythonKnowledgeParser(fact_memory=fact_memory)
        else:
            raise NotImplementedError(f"{language} parsing not implemented")

    def add_folders(
            self,
            folders: List[str],
        ):
        for i, folder in enumerate(folders):
            folder_name = os.path.basename(folder)
            for dirpath, dirnames, filenames in os.walk(folder):
                for filename in filenames:
                    if not filename.startswith("."):
                        if filename.endswith(self.extension):
                            source = os.path.join(dirpath, filename)
                            try:
                                f = open(source, "r")
                                file_content = f.read()
                                self.parser.parse(filename, file_content)
                            except Exception:
                                continue