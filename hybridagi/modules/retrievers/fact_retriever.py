import dspy
from abc import abstractmethod
from hybridagi.core.datatypes import Query, QueryWithFacts

class FactRetriever(dspy.Module):
    
    @abstractmethod
    def forward(self, query: Query) -> QueryWithFacts:
        raise NotImplementedError(
            f"FactRetriever {type(self).__name__} is missing the required 'forward' method."
        )