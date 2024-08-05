import dspy
from abc import abstractmethod
from hybridagi.core.datatypes import Query, QueryWithGraphPrograms

class GraphProgramRetriever(dspy.Module):
    
    @abstractmethod
    def forward(self, query: Query) -> QueryWithGraphPrograms:
        raise NotImplementedError(
            f"GraphProgramRetriever {type(self).__name__} is missing the required 'forward' method."
        )