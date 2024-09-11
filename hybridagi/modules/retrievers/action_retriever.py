import dspy
from abc import abstractmethod
from typing import Union
from hybridagi.core.datatypes import Query, QueryList, QueryWithSteps

class ActionRetriever(dspy.Module):
    
    @abstractmethod
    def forward(self, query_or_queries: Union[Query, QueryList]) -> QueryWithSteps:
        raise NotImplementedError(
            f"ActionRetriever {type(self).__name__} is missing the required 'forward' method."
        )