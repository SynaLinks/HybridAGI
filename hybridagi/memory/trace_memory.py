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
    def is_finished(self, program_id: Union[UUID, str]) -> bool:
        raise NotImplementedError(
            f"TraceMemory {type(self).__name__} is missing the required 'is_finished' method."
        )
       
    @abstractmethod
    def clear(self):
        raise NotImplementedError(
            f"TraceMemory {type(self).__name__} is missing the required 'clear' method."
        )