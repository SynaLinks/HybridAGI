from abc import ABC, abstractmethod
from typing import Union, List
from uuid import UUID
from hybridagi.core.datatypes import AgentStep, AgentStepList

class TraceMemory(ABC):
    
    @abstractmethod
    def exist(self, step_id) -> bool:
        raise NotImplementedError(
            f"FactMemory {type(self).__name__} is missing the required 'exist' method."
        )

    @abstractmethod
    def update(self, step_or_steps: Union[AgentStep, AgentStepList]) -> None:
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