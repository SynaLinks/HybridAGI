import dspy
from abc import abstractmethod
from hybridagi.core.datatypes import QueryWithDocuments

class DocumentReranker(dspy.Module):
    
    @abstractmethod
    def forward(self, query: QueryWithDocuments) -> QueryWithDocuments:
        raise NotImplementedError(
            f"DocumentReranker {type(self).__name__} is missing the required 'forward' method."
        )