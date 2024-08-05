import dspy
from abc import abstractmethod
from hybridagi.core.datatypes import Query, QueryWithDocuments

class DocumentRetriever(dspy.Module):
    
    @abstractmethod
    def forward(self, query: Query) -> QueryWithDocuments:
        raise NotImplementedError(
            f"DocumentRetriever {type(self).__name__} is missing the required 'forward' method."
        )