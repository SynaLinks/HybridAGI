import dspy
import numpy as np
from enum import Enum
from typing import Optional
import faiss
from hybridagi.memory import FactMemory
from hybridagi.embeddings import Embeddings
from hybridagi.core.datatypes import Query, QueryWithFacts
from hybridagi.modules.retrievers import FactRetriever
from hybridagi.modules.rerankers import FactReranker

class EmbeddingsDistance(str, Enum):
    Cosine = "cosine"
    Euclidean = "euclidean"

class FAISSFactRetriever(FactRetriever):
    
    def __init__(
            self,
            fact_memory: FactMemory,
            embeddings: Embeddings,
            distance: str = "cosine",
            max_distance: float = 0.7,
            k: int = 5,
            reranker: Optional[FactReranker] = None,
        ):
        self.fact_memory = fact_memory
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
    
    def forward(self, query: Query) -> QueryWithFacts:
        if not isinstance(query, Query):
            raise ValueError(f"{type(self).__name__} input must be a Query")
        result = QueryWithFacts()
        result.query.query = query.query
        embeddings_map = self.fact_memory._facts_embeddings
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
                    fact_index = indexes[0][i]
                    fact_id = list(embeddings_map.keys())[fact_index]
                    fact = self.fact_memory.get_facts(fact_id).facts[0]
                    result.facts.append(fact)
                else:
                    break
            if self.reranker is not None:
                return self.reranker(result)
        return result