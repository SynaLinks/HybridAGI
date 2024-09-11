import dspy
from abc import abstractmethod
from typing import Union
from hybridagi.core.datatypes import Query, QueryList, QueryWithDocuments

class DocumentRetriever(dspy.Module):
    
    @abstractmethod
    def forward(self, query_or_queries: Union[Query, QueryList]) -> QueryWithDocuments:
        raise NotImplementedError(
            f"DocumentRetriever {type(self).__name__} is missing the required 'forward' method."
        )