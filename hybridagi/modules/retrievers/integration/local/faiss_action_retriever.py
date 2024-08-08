import dspy
import numpy as np
from enum import Enum
from typing import Optional
import faiss
from hybridagi.memory import TraceMemory
from hybridagi.embeddings import Embeddings
from hybridagi.core.datatypes import Query, QueryWithSteps
from hybridagi.modules.retrievers import ActionRetriever
from hybridagi.modules.rerankers import ActionReranker

class EmbeddingsDistance(str, Enum):
    Cosine = "cosine"
    Euclidean = "euclidean"

class FAISSActionRetriever(ActionRetriever):
    """
    A class for retrieving actions using FAISS (Facebook AI Similarity Search) and embeddings.

    Parameters:
        trace_memory (TraceMemory): An instance of TraceMemory class which stores the memory of the agent.
        embeddings (Embeddings): An instance of Embeddings class which is used to convert text into numerical vectors.
        distance (str, optional): The distance metric to use for similarity search. Should be either "cosine" or "euclidean". Defaults to "cosine".
        max_distance (float, optional): The maximum distance threshold for considering an action as a match. Defaults to 0.9.
        k (int, optional): The number of nearest neighbors to retrieve. Defaults to 5.
        reranker (Optional[ActionReranker], optional): An instance of ActionReranker class which is used to re-rank the retrieved actions. Defaults to None.
    """
    
    def __init__(
            self,
            trace_memory: TraceMemory,
            embeddings: Embeddings,
            distance: str = "cosine",
            max_distance: float = 0.9,
            k: int = 5,
            reranker: Optional[ActionReranker] = None,
        ):
        self.trace_memory = trace_memory
        self.embeddings = embeddings
        if distance == EmbeddingsDistance.Cosine:
            self.distance = EmbeddingsDistance.Cosine
        elif distance == EmbeddingsDistance.Euclidean:
            self.distance = EmbeddingsDistance.Euclidean
        else:
            raise ValueError("Invalid distance provided, should be cosine or euclidean") 
        self.max_distance = max_distance
        self.reranker = reranker
        self.k = k
        vector_dim = self.embeddings.dim
        if self.distance == "euclidean":
            self.index = faiss.IndexFlatL2(vector_dim)
        else:
            self.index = faiss.IndexFlatIP(vector_dim)
    
    def forward(self, query: Query) -> QueryWithSteps:
        """
        Retrieve actions based on the given query.

        Parameters:
            query (Query): An instance of Query class which contains the query text.

        Returns:
            QueryWithSteps: An instance of QueryWithSteps class which contains the query text and the retrieved actions.
        """
        if not isinstance(query, Query):
            raise ValueError(f"{type(self).__name__} input must be a Query")
        result = QueryWithSteps()
        result.query.query = query.query
        embeddings_map = self.trace_memory._embeddings
        vectors = np.array(list(embeddings_map.values()), dtype="float32")
        if vectors.shape[0] > 0:
            self.index.reset()
            if self.distance == "euclidean":
                faiss.normalize_L2(vectors)
            self.index.add(vectors)
            query_vector = np.array([self.embeddings.embed_text(query.query)], dtype="float32")
            distances, indexes = self.index.search(query_vector, min(vectors.shape[0], self.k))
            for i in range(min(vectors.shape[0], self.k)):
                if distances[0][i] < self.max_distance:
                    action_index = indexes[0][i]
                    action_id = list(embeddings_map.keys())[action_index]
                    action = self.trace_memory.get(action_id).steps[0]
                    result.steps.append(action)
                else:
                    break
            if self.reranker is not None:
                return self.reranker(result)
        return result