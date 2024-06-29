from typing import Optional
from .base import BaseKnowledgeParser
from ..hybridstores.fact_memory.fact_memory import FactMemory
from ..hybridstores.filesystem.filesystem import FileSystem

class TextKnowledgeParser(BaseKnowledgeParser):

    def __init__(
            self,
            filesystem: FileSystem,
            fact_memory: FactMemory,
        ):
        super().__init__(
            filesystem = filesystem,
            fact_memory = fact_memory,
            valid_extensions = [".txt", ".md"],
        )

    def parse(self, dest_path:str, content: str):
        self.filesystem.add_texts(
            texts=[content],
            ids=[dest_path],
        )
        # TODO add triplet extraction for the fact memory

    def read(self, source_path: str) -> str:
        f = open(source_path, "r")
        file_content = f.read()
        return file_content