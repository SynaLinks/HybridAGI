import dspy
from abc import abstractmethod
from typing import Union
from hybridagi.core.datatypes import Query, QueryList, QueryWithEntities

class EntityRetriever(dspy.Module):
    
    @abstractmethod
    def forward(self, query_or_queries: Union[Query, QueryList]) -> QueryWithEntities:
        raise NotImplementedError(
            f"EntityRetriever {type(self).__name__} is missing the required 'forward' method."
        )