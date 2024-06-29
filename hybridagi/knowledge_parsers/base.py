import os
import abc
from typing import List, Optional
from ..hybridstores.filesystem.filesystem import FileSystem
from ..hybridstores.fact_memory.fact_memory import FactMemory

class BaseKnowledgeParser():

    def __init__(
            self,
            filesystem: FileSystem,
            fact_memory: FactMemory,
            valid_extensions: List[str] = [],
        ):
        self.filesystem = filesystem
        self.fact_memory = fact_memory
        self.valid_extensions = valid_extensions

    @abc.abstractmethod
    def parse(self, dest_path: str, content: str):
        pass

    def read(self, source_path: str) -> str:
        pass
