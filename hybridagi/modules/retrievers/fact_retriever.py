import dspy
from abc import abstractmethod
from typing import Union
from hybridagi.core.datatypes import Query, QueryList, QueryWithFacts

class FactRetriever(dspy.Module):
    
    @abstractmethod
    def forward(self, query_or_queries: Union[Query, QueryList]) -> QueryWithFacts:
        raise NotImplementedError(
            f"FactRetriever {type(self).__name__} is missing the required 'forward' method."
        )