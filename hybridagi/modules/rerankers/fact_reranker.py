import dspy
from abc import abstractmethod
from hybridagi.core.datatypes import QueryWithFacts

class FactReranker(dspy.Module):
    
    @abstractmethod
    def forward(self, query: QueryWithFacts) -> QueryWithFacts:
        raise NotImplementedError(
            f"FactReranker {type(self).__name__} is missing the required 'forward' method."
        )