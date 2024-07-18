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