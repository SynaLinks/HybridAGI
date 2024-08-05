import dspy
from abc import abstractmethod
from hybridagi.core.datatypes import QueryWithSteps

class ActionReranker(dspy.Module):
    
    @abstractmethod
    def forward(self, query: QueryWithSteps) -> QueryWithSteps:
        raise NotImplementedError(
            f"ActionReranker {type(self).__name__} is missing the required 'forward' method."
        )