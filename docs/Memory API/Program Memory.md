
The program memory is where the the Agent system store each plan, in our innovative solution, we decided to see planning as the execution of graph software. Making more reliable our solution (as opposed to React agents) while giving the system *algorithmic flexibility*.

The Agent have a *deterministic plan* that it will execute reliably, you can see the execution of the plan as a navigation task for the Agent where it have to decide at each decision step which branch to take to complete the task.

Because it can only execute plans it have in memory, the system can only learn on the fly new plans by programming itself. However, for businesses we encourage them to *build the programs themselves* as self-programming agents is still an open research problem.


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