import dspy
from abc import abstractmethod
from hybridagi.core.datatypes import Query, QueryWithEntities

class EntityRetriever(dspy.Module):
    
    @abstractmethod
    def forward(self, query: Query) -> QueryWithEntities:
        raise NotImplementedError(
            f"EntityRetriever {type(self).__name__} is missing the required 'forward' method."
        )