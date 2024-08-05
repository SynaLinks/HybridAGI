from abc import ABC, abstractmethod
from typing import Any
from hybridagi.core.datatypes import DocumentList

class DocumentReader(ABC):

    @abstractmethod
    def read(self, filepath: str) -> DocumentList:
        pass
    
    def __call__(self, filepath: str) -> DocumentList:
        return self.read(filepath)