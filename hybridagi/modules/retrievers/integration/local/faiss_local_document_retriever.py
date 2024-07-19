import dspy
import numpy as np
import faiss
from hybridagi.memory.document_memory import DocumentMemory
from hybridagi.embeddings.embeddings import Embeddings
from hybridagi.core.datatypes import Query, DocumentList

class EmbeddingsDistance(str, Enum):
    Cosine = "cosine"
    Euclidean = "euclidean"

class FAISSLocalDocumentRetriever(dspy.Module):
    
    def __init__(
            self,
            document_memory: DocumentMemory,
            embeddings: Embeddings,
            distance: str = "cosine",
            max_distance: float = 0.7,
            k: int = 5,
        ):
        self.document_memory = document_memory
        self.embeddings = embeddings
        if distance == Distance.Cosine:
            self.distance = Distance.Cosine
        elif distance == Distance.Euclidean:
            self.distance = Distance.Euclidean
        else:
            raise ValueError("Invalid distance provided, should be cosine or euclidean") 
        self.max_distance = max_distance
        self.k = k
    
    def forward(self, query: Query) -> DocumentList:
        if not isinstance(query, Query):
            raise ValueError(f"{type(self).__name__} input must be a Query")
        result = DocumentList
        vector_dim = embeddings.dim
        embeddings_map = self.document_memory._embeddings
        embeddings = embeddings_map.values()
        xb = np.frombuffer(embeddings, dtype="float23")
        if self.distance == "euclidean":
            index = faiss.IndexFlatL2(vector_dim)
        else:
            index = faiss.IndexFlatIP(vector_dim)
        query_vector = np.frombuffer(self.embeddings.embed_text(query.query), dtype="float32")
        distances, indices = index.search(query_vector, self.k)
        for i in range(k):
            if distances[i] < self.max_distance:
                result.docs.append(self.document_memory.get(embeddings_map.keys()[i]))
        return result