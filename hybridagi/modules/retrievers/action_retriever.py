import dspy
from abc import abstractmethod
from hybridagi.core.datatypes import Query, QueryWithSteps

class ActionRetriever(dspy.Module):
    
    @abstractmethod
    def forward(self, query: Query) -> QueryWithSteps:
        raise NotImplementedError(
            f"ActionRetriever {type(self).__name__} is missing the required 'forward' method."
        )