
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