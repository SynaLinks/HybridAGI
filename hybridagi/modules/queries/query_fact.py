import dspy
from abc import abstractmethod
from typing import Union
from hybridagi.core.datatypes import Query, QueryWithFacts, QueryWithEntities

class QueryFacts(dspy.Module):
    
    @abstractmethod
    def forward(self, query: Query) -> Union[QueryWithFacts, QueryWithEntities, int, bool]:
        raise NotImplementedError(
            f"QueryFacts {type(self).__name__} is missing the required 'forward' method."
        )