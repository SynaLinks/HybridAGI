import dspy
from typing import Union, Optional, List
from dsp.utils import dotdict
from ..embeddings.base import BaseEmbeddings
from ..hybridstores.trace_memory.trace_memory import TraceMemory

class ActionRetriever(dspy.Retrieve):
    """Retrieve past actions based on similarity"""

    def __init__(
            self,
            trace_memory: TraceMemory,
            embeddings: BaseEmbeddings,
            distance_threshold: float = 1.0,
            k: int = 3,
        ):
        """The retriever constructor"""
        super().__init__(k = k)
        self.trace_memory = trace_memory
        self.embeddings = embeddings
        self.distance_threshold = distance_threshold

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
                "CALL db.idx.vector.queryNodes('"+self.trace_memory.indexed_label+"', 'embeddings_vector', $k, vecf32($vector)) YIELD node, score",
                "RETURN node.name AS name, score"])
            result = self.trace_memory.hybridstore.query(
                query,
                params = params,
            )
            print(result.result_set)
            if len(result.result_set) > 0:
                for record in result.result_set:
                    content = self.trace_memory.get_content(record[0])
                    distance = float(record[1])
                    if distance < self.distance_threshold:
                        contents.extend([{"actions": dotdict({"past_action": content}), "distance": distance}])
        sorted_passages = sorted(
            contents,
            key=lambda x: x["distance"],
            reverse=True,
        )[: k or self.k]
        return dspy.Prediction(
            past_actions=[el["actions"] for el in sorted_passages]
        )