import dspy
import numpy as np
from enum import Enum
from typing import Optional
import faiss
from hybridagi.memory import DocumentMemory
from hybridagi.embeddings import Embeddings
from hybridagi.core.datatypes import Query, QueryWithDocuments
from hybridagi.modules.retrievers import DocumentRetriever
from hybridagi.modules.rerankers import DocumentReranker

class EmbeddingsDistance(str, Enum):
    Cosine = "cosine"
    Euclidean = "euclidean"

class FAISSDocumentRetriever(DocumentRetriever):
    """
    A class for retrieving documents using FAISS (Facebook AI Similarity Search) and embeddings.

    Parameters:
        document_memory (DocumentMemory): An instance of DocumentMemory class which stores the documents.
        embeddings (Embeddings): An instance of Embeddings class which is used to convert text into numerical vectors.
        distance (str, optional): The distance metric to use for similarity search. Should be either "cosine" or "euclidean". Defaults to "cosine".
        max_distance (float, optional): The maximum distance threshold for considering a document as a match. Defaults to 0.7.
        k (int, optional): The number of nearest neighbors to retrieve. Defaults to 5.
        reranker (Optional[DocumentReranker], optional): An instance of DocumentReranker class which is used to re-rank the retrieved documents. Defaults to None.
    """
    
    def __init__(
            self,
            document_memory: DocumentMemory,
            embeddings: Embeddings,
            distance: str = "cosine",
            max_distance: float = 0.7,
            k: int = 5,
            reranker: Optional[DocumentReranker] = None,
        ):
        self.document_memory = document_memory
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
    
    def forward(self, query: Query) -> QueryWithDocuments:
        """
        Retrieve documents based on the given query.

        Parameters:
            query (Query): An instance of Query class which contains the query text.

        Returns:
            QueryWithDocuments: An instance of QueryWithDocuments class which contains the query text and the retrieved documents.
        """
        if not isinstance(query, Query):
            raise ValueError(f"{type(self).__name__} input must be a Query")
        result = QueryWithDocuments()
        result.query.query = query.query
        embeddings_map = self.document_memory._embeddings
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
                    document_index = indexes[0][i]
                    document_id = list(embeddings_map.keys())[document_index]
                    document = self.document_memory.get(document_id).docs[0]
                    result.docs.append(document)
                else:
                    break
            if self.reranker is not None:
                return self.reranker(result)
        return result