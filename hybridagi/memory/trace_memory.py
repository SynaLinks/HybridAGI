from abc import ABC, abstractmethod
from typing import Union, List
from uuid import UUID
from hybridagi.core.datatypes import AgentStep, AgentStepList

class TraceMemory(ABC):
    
    @abstractmethod
    def exist(self, step_id: Union[UUID, str]) -> bool:
        raise NotImplementedError(
            f"FactMemory {type(self).__name__} is missing the required 'exist' method."
        )

    @abstractmethod
    def update(self, step_or_steps: Union[AgentStep, AgentStepList]) -> None:
        raise NotImplementedError(
            f"TraceMemory {type(self).__name__} is missing the required 'update' method."
        )

    @abstractmethod
    def get(self, id_or_ids: Union[UUID, str, List[Union[UUID, str]]]) -> AgentStepList:
        raise NotImplementedError(
            f"TraceMemory {type(self).__name__} is missing the required 'get' method."
        )

    @abstractmethod
    def clear(self):
        raise NotImplementedError(
            f"TraceMemory {type(self).__name__} is missing the required 'clear' method."
        )