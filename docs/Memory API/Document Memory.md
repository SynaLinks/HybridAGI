
The document memory is where the Agent store unstructured knowledge, it allow the system to retrieve texts to answer precisely about contextual question.

We provide the following interface for you to implement your own integration.

```python
from abc import ABC, abstractmethod
from typing import Union, List
from uuid import UUID
from hybridagi.core.datatypes import Document, DocumentList

class DocumentMemory(ABC):

    @abstractmethod
    def update(self, doc_or_docs: Union[Document, DocumentList]) -> None:
        raise NotImplementedError(
            f"DocumentMemory {type(self).__name__} is missing the required 'update' method."
        )

    @abstractmethod
    def remove(self, id_or_ids: Union[UUID, str, List[Union[UUID, str]]]) -> None:
        raise NotImplementedError(
            f"DocumentMemory {type(self).__name__} is missing the required 'remove' method."
        )

    @abstractmethod
    def get(self, id_or_ids: Union[UUID, str, List[Union[UUID, str]]]) -> DocumentList:
        raise NotImplementedError(
            f"DocumentMemory {type(self).__name__} is missing the required 'get' method."
        )
    
    @abstractmethod
    def get_parents(self, id_or_ids: Union[UUID, str, List[Union[UUID, str]]]) -> DocumentList:
        raise NotImplementedError(
            f"DocumentMemory {type(self).__name__} is missing the required 'get_parent' method."
        )
    
    @abstractmethod
    def clear(self):
        raise NotImplementedError(
            f"DocumentMemory {type(self).__name__} is missing the required 'clear' method."
        )
```