import dspy
from typing import Union, Optional, List
from dsp.utils import dotdict
from ..embeddings.base import BaseEmbeddings
from ..hybridstores.program_memory.program_memory import ProgramMemory

class ProgramRetriever(dspy.Retrieve):
    """Retrieve program names and description based on similarity"""

    def __init__(
            self,
            program_memory: ProgramMemory,
            embeddings: BaseEmbeddings,
            k: int = 3,
        ):
        """The retriever constructor"""
        super().__init__(k = k)
        self.program_memory = program_memory
        self.embeddings = embeddings

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
            #TODO update the Cypher query to only return the non-protected programs
            query = " ".join([
                "CALL db.idx.vector.queryNodes('"+self.program_memory.indexed_label+"', 'embeddings_vector', $k, vecf32($vector)) YIELD node, score",
                "RETURN node.name AS name, node.description AS description, score"])
            result = self.program_memory.hybridstore.query(
                query,
                params = params,
            )
            contents.extend(
                [{"passage": dotdict({"subprogram": f"{r[0]}: {r[1]}"}), "score": r[2]}
                for r in result.result_set])
            print(contents)
        sorted_passages = sorted(
            contents,
            key=lambda x: x["score"],
            reverse=True,
        )[: k or self.k]
        return dspy.Prediction(
            passages=[el["passage"] for el in sorted_passages]
        )