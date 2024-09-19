"""The graph program retriever. Copyright (C) 2024 Yoan Sallami - SynaLinks. License: GPL-3.0"""

import numpy as np
import dspy
from typing import Union, Optional, List
from dsp.utils import dotdict
from hybridagi.embeddings import Embeddings
from hybridagi.memory import ProgramMemory
from hybridagi.modules.retrievers import GraphProgramRetriever
from hybridagi.core.datatypes import Query, QueryList, QueryWithGraphPrograms
from hybridagi.core.pipeline import Pipeline

class FalkorDBGraphProgramRetriever(GraphProgramRetriever):
    """
    A class for retrieving documents using FalkorDB approximate nearest neighbor vector search.

    Parameters:
        program_memory (GraphProgramMemory): An instance of GraphProgramMemory class which stores the memory of the agent.
        embeddings (Embeddings): An instance of Embeddings class which is used to convert text into numerical vectors.
        distance (str, optional): The distance metric to use for similarity search. Should be either "cosine" or "euclidean". Defaults to "cosine".
        max_distance (float, optional): The maximum distance threshold for considering an action as a match. Defaults to 0.9.
        k (int, optional): The number of nearest neighbors to retrieve. Defaults to 5.
        reverse (bool, optional): Weither or not to reverse the final result. Default to True.
        reranker (Optional[Pipeline], optional): An instance of Pipeline class which is used to re-rank the retrieved graph programs. Defaults to None.
    """

    def __init__(
            self,
            program_memory: ProgramMemory,
            embeddings: Embeddings,
            distance: str = "cosine",
            max_distance: float = 0.9,
            k: int = 5,
            reverse: bool = True,
            reranker: Optional[Pipeline] = None,
        ):
        """The retriever constructor"""
        self.program_memory = program_memory
        self.embeddings = embeddings
        if distance != "cosine" and distance != "euclidean":
            raise ValueError("Invalid distance provided, should be cosine or euclidean")
        self.distance = distance
        self.max_distance = max_distance
        self.reranker = reranker
        self.k = k
        self.reverse = reverse
        try:
            params = {"dim": self.embeddings.dim, "distance": self.distance}
            self.program_memory._graph.query(
                "CREATE VECTOR INDEX FOR (p:GraphProgram) ON (p.vector) OPTIONS {dimension:$dim, similarityFunction:$distance}",
                params,
            )
        except Exception:
            pass

    def forward(self, query_or_queries: Union[Query, QueryList]) -> QueryWithGraphPrograms:
        """
        Retrieve actions based on the given query.

        Parameters:
            query_or_queries (Union[Query, QueryList]): An instance of Query or QueryList class which contains the query text.

        Returns:
            QueryWithGraphPrograms: An instance of QueryWithGraphPrograms class which contains the query text and the retrieved graph programs.
        """
        if not isinstance(query_or_queries, (Query, QueryList)):
            raise ValueError(f"{type(self).__name__} input must be a Query or QueryList")
        if isinstance(query_or_queries, Query):
            queries = QueryList()
            queries.queries = [query_or_queries]
        else:
            queries = query_or_queries
        result = QueryWithGraphPrograms()
        result.queries.queries = queries.queries
        query_vectors = self.embeddings.embed_text([q.query for q in queries.queries])
        items = []
        indexes = {}
        for vector in query_vectors:
            params = {"vector": list(vector), "k": int(2*self.k)}
            query = " ".join([
                'CALL db.idx.vector.queryNodes("GraphProgram", "vector", $k, vecf32($vector)) YIELD node, score',
                'RETURN node.id AS id, score'])
            query_result = self.program_memory._graph.query(
                query,
                params = params,
            )
            if len(query_result.result_set) > 0:
                for record in query_result.result_set:
                    if record[0] not in indexes:
                        indexes[record[0]] = True
                    else:
                        continue
                    programs_list = self.program_memory.get(record[0])
                    distance = float(record[1])
                    if distance < self.max_distance:
                        items.extend([{"prog": programs_list.progs[0], "distance": distance}])
        if len(items) > 0:
            sorted_items = sorted(
                items,
                key = lambda x: x["distance"],
                reverse = False,
            )[:self.k]
            result.progs = [i["prog"] for i in sorted_items]
            if self.reranker is not None:
                result = self.reranker(result)
            if self.reverse:
                result.progs.reverse()
        return result