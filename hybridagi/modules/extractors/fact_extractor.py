import dspy
from abc import abstractmethod
from typing import Union
from hybridagi.core.datatypes import Document, DocumentList, FactList

class FactExtractor(dspy.Module):
    
    @abstractmethod
    def forward(self, doc_or_docs: Union[Document, DocumentList])-> FactList:
        pass