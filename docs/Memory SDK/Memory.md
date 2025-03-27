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

## Program Memory

The program memory is where the the Agent system store each graph program, in our innovative solution, we decided to see planning as the execution of turing complete DSL describing a graph software. Making more reliable and customizable our solution (as opposed to React agents) while giving the system the required *flexibility* to handle many usecases.

The Agent have a *deterministic program* that it will execute reliably, you can see the execution of the program as a navigation task for the Agent where it have to decide at each decision step which branch to take to complete the task.

Because it can only execute plans it have in memory, the system can only learn on the fly new methodologies by programming itself. However, for businesses we encourage them to *build the programs themselves* as self-programming agents is still an open research problem.

```python
from abc import ABC, abstractmethod
from typing import Union, List
from uuid import UUID
from hybridagi.core.graph_program import GraphProgram, GraphProgramList

class ProgramMemory(ABC):

    @abstractmethod
    def update(self, doc_or_docs: Union[GraphProgram, GraphProgramList]) -> None:
        raise NotImplementedError(
            f"ProgramMemory {type(self).__name__} is missing the required 'update' method."
        )

    @abstractmethod
    def remove(self, id_or_ids: Union[UUID, str, List[Union[UUID, str]]]) -> None:
        raise NotImplementedError(
            f"ProgramMemory {type(self).__name__} is missing the required 'remove' method."
        )

    @abstractmethod
    def get(self, id_or_ids: Union[UUID, str, List[Union[UUID, str]]]) -> GraphProgramList:
        raise NotImplementedError(
            f"ProgramMemory {type(self).__name__} is missing the required 'get' method."
        )
    
    @abstractmethod
    def get_dependencies(self, id_or_ids: Union[UUID, str, List[Union[UUID, str]]]) -> List[str]:
        raise NotImplementedError(
            f"ProgramMemory {type(self).__name__} is missing the required 'get_dependencies' method."
        )
    
    @abstractmethod
    def depends_on(self, source_id: Union[UUID, str], target_id: Union[UUID, str]) -> List[str]:
        raise NotImplementedError(
            f"ProgramMemory {type(self).__name__} is missing the required 'depends_on' method."
        )
        
    @abstractmethod
    def clear(self):
        raise NotImplementedError(
            f"ProgramMemory {type(self).__name__} is missing the required 'clear' method."
        )
```

## Trace Memory

The trace memory is where the Agent system store each executed step of the graph programs, it allow the system to recall actions between session, very much like the human episodic memory that allow us to remember past events and actions we performed.

```python
from abc import ABC, abstractmethod
from typing import Union, List
from uuid import UUID
from hybridagi.core.datatypes import AgentStep, AgentStepList

class TraceMemory(ABC):

    @abstractmethod
    def update(self, doc_or_docs: Union[AgentStep, AgentStepList]) -> None:
        raise NotImplementedError(
            f"TraceMemory {type(self).__name__} is missing the required 'update' method."
        )

    @abstractmethod
    def remove(self, id_or_ids: Union[UUID, str, List[Union[UUID, str]]]) -> None:
        raise NotImplementedError(
            f"TraceMemory {type(self).__name__} is missing the required 'remove' method."
        )

    @abstractmethod
    def get(self, id_or_ids: Union[UUID, str, List[Union[UUID, str]]]) -> AgentStepList:
        raise NotImplementedError(
            f"TraceMemory {type(self).__name__} is missing the required 'get' method."
        )
        
    @abstractmethod
    def get_trace(self, id: Union[UUID, str]) -> AgentStepList:
        raise NotImplementedError(
            f"TraceMemory {type(self).__name__} is missing the required 'get_trace' method."
        )
       
    @abstractmethod
    def clear(self):
        raise NotImplementedError(
            f"TraceMemory {type(self).__name__} is missing the required 'clear' method."
        )
```