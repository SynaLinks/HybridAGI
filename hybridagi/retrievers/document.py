import dspy
from typing import Union, Optional, List
from dsp.utils import dotdict
from ..embeddings.base import BaseEmbeddings
from .base import BaseRetriever

class DocumentRetriever(BaseRetriever):
    """Retrieve document chunks based on similarity"""

    def __init__(
            self,
            index_name: str,
            embeddings: BaseEmbeddings,
            graph_index: str = "filesystem",
            hostname: str = "localhost",
            port: int = 6379,
            username: str = "",
            password: str = "",
            indexed_label: str = "Content",
            k: int = 3,
        ):
        """The retriever constructor"""
        super().__init__(
            index_name = index_name,
            graph_index = graph_index,
            embeddings = embeddings,
            hostname = hostname,
            port = port,
            username = username,
            password = password,
            indexed_label = indexed_label,
            k = k,
        )

    def forward(
            self,
            query_or_queries: Union[str, List[str]],
            k:Optional[int] = None,
        ) -> dspy.Prediction:
        """Method to perform DSPy forward prediction"""
        if not isinstance(query_or_queries, list):
            query_or_queries = [query_or_queries]
        query_vectors = self.embeddings.embed_text(query_or_queries)
        contents = []
        for vector in query_vectors:
            params = {"vector": list(vector), "k": k or self.k}
            query = " ".join([
                "CALL db.idx.vector.queryNodes('"+self.indexed_label+"', 'embeddings_vector', $k, vecf32($vector)) YIELD node, score",
                "RETURN node.name AS name, score"])
            result = self.hybridstore.query(
                query,
                params = params,
            )
            contents.extend(
                [{"passage": dotdict({"long_text": self.get_content(r[0])}), "score": r[1]} 
                for r in result.result_set])
        sorted_passages = sorted(
            contents,
            key=lambda x: x["score"],
            reverse=True,
        )[: k or self.k]
        return dspy.Prediction(
            passages=[el["passage"] for el in sorted_passages]
        )