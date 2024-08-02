from abc import abstractmethod
import dspy
from typing import Union
from hybridagi.core.datatypes import Document, DocumentList

class DocumentSplitter(dspy.Module):
    
    @abstractmethod
    def forward(self, doc_or_docs: Union[Document, DocumentList]) -> DocumentList:
        raise NotImplementedError(
            f"DocumentSplitter {type(self).__name__} is missing the required 'forward' method."
        )