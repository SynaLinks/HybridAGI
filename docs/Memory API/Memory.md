# Memory

The long-term memory is critical component of any Agentic system, not just Agentic RAG. Because classic neural networks cannot learn on the fly, you have to combine them with an external memory system in order for them to operate in changing enviroment but also to be able to learn new knowledge (or now methodologies).

## Document Memory

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

## Fact Memory


The fact memory is where the Agent store structured knowledge in the form of facts, it allows the system to retrieve precise and relevant information to factual questions.

Like for the document memory, we provide an interface to allows you to integrate with the graph database of your choice.

```python
from abc import ABC, abstractmethod
from typing import Union, List
from uuid import UUID
from hybridagi.core.datatypes import Entity, EntityList
from hybridagi.core.datatypes import Fact, FactList

class FactMemory(ABC):

    @abstractmethod
    def update(self, entities_or_facts: Union[Entity, EntityList, Fact, FactList]) -> None:
        raise NotImplementedError(
            f"DocumentMemory {type(self).__name__} is missing the required 'update' method."
        )

    @abstractmethod
    def remove(self, id_or_ids: Union[UUID, str, List[Union[UUID, str]]]) -> None:
        raise NotImplementedError(
            f"DocumentMemory {type(self).__name__} is missing the required 'remove' method."
        )

    @abstractmethod
    def get_entities(self, id_or_ids: Union[UUID, str, List[Union[UUID, str]]]) -> EntityList:
        raise NotImplementedError(
            f"FactMemory {type(self).__name__} is missing the required 'get_entities' method."
        )
    
    @abstractmethod
    def get_facts(self, id_or_ids: Union[UUID, str, List[Union[UUID, str]]]) -> FactList:
        raise NotImplementedError(
            f"FactMemory {type(self).__name__} is missing the required 'get_facts' method."
        )
        
    @abstractmethod
    def clear(self):
        raise NotImplementedError(
            f"FactMemory {type(self).__name__} is missing the required 'clear' method."
        )
```