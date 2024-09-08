from abc import ABC, abstractmethod
from typing import Union, List
from uuid import UUID
from hybridagi.core.graph_program import GraphProgram
from hybridagi.core.datatypes import GraphProgramList

class ProgramMemory(ABC):
    
    @abstractmethod
    def exist(self, prog_id: Union[UUID, str]) -> bool:
        raise NotImplementedError(
            f"ProgramMemory {type(self).__name__} is missing the required 'exist' method."
        )

    @abstractmethod
    def update(self, prog_or_progs: Union[GraphProgram, GraphProgramList]) -> None:
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
    def depends_on(self, source_id: Union[UUID, str], target_id: Union[UUID, str]) -> bool:
        raise NotImplementedError(
            f"ProgramMemory {type(self).__name__} is missing the required 'depends_on' method."
        )
        
    def is_protected(self, name: str) -> bool:
        """
        Returns True if the main program depends on the given program False otherwise
        """
        return self.depends_on("main", name)
        
    @abstractmethod
    def clear(self):
        raise NotImplementedError(
            f"ProgramMemory {type(self).__name__} is missing the required 'clear' method."
        )