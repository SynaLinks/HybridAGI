"""The entity retriever. Copyright (C) 2024 SynaLinks. License: GPL-3.0"""

import numpy as np
import dspy
from typing import Union, Optional, List
from dsp.utils import dotdict
from ..embeddings.base import BaseEmbeddings
from ..hybridstores.fact_memory.fact_memory import FactMemory

class EntityRetriever(dspy.Retrieve):
    """Retrieve entities based on similarity"""

    def __init__(
            self,
            fact_memory: FactMemory,
            embeddings: BaseEmbeddings,
            distance_threshold: float = 1.2,
            k: int = 3,
        ):
        """The retriever constructor"""
        super().__init__(k = k)
        self.fact_memory = fact_memory
        self.embeddings = embeddings
        self.distance_threshold = distance_threshold

    def forward(
            self,
            query_or_queries: Union[str, List[str]],
            k: Optional[int] = None,
        ) -> dspy.Prediction:
        """Method to perform DSPy forward prediction"""
        if not isinstance(query_or_queries, list):
            query_or_queries = [query_or_queries]
        query_vectors = self.embeddings.embed_text(query_or_queries)
        contents = []
        indexes = {}
        for vector in query_vectors:
            # For an obscure reason falkordb needs a bigger k to find more indexed items
            params = {"indexed_label": self.fact_memory.indexed_label, "vector": list(vector), "k": 2*int(k or self.k)}
            query = " ".join([
                'CALL db.idx.vector.queryNodes($indexed_label, "embeddings_vector", $k, vecf32($vector)) YIELD node, score',
                'RETURN node.name AS name, node.description AS description, score'])
            result = self.fact_memory.hybridstore.query(
                query,
                params = params,
            )
            if len(result.result_set) > 0:
                for record in result.result_set:
                    if record[0] not in indexes:
                        indexes[record[0]] = True
                    else:
                        continue
                    name = record[0]
                    text = self.fact_memory.get_content(record[0])
                    description = record[1]
                    metadata = self.filesystem.get_content_metadata(record[0])
                    distance = float(record[2])
                    if distance < self.distance_threshold:
                        contents.extend([{"entities": dotdict({"entity": name, "description": description, "text": text, "metadata": metadata}), "distance": distance}])
        sorted_passages = sorted(
            contents,
            key=lambda x: x["distance"],
            reverse=False,
        )[: k or self.k]
        return dspy.Prediction(
            entities=[el["entities"] for el in sorted_passages]
        )