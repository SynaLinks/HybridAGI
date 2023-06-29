"""The hybrid vector/graph storage. Copyright (C) 2023 SynaLinks. License: GPL-3.0"""

import uuid
import numpy as np
from typing import Callable, Type, Optional, Any, Dict
from langchain.vectorstores.redis import Redis
from redisgraph import Graph

def _default_relevance_score(val: float) -> float:
    return 1 - val

class RedisGraphHybridStore(Redis):
    """The RedisGraph hybrid vector/graph store"""
    def __init__(
        self,
        redis_url: str,
        index_name: str,
        embedding_function: Callable,
        content_key: str = "content",
        metadata_key: str = "metadata",
        vector_key: str = "content_vector",
        graph_key: str = "graph",
        program_key: str = "program",
        relevance_score_fn: Optional[
            Callable[[float], float]
        ] = _default_relevance_score,
        **kwargs: Any,
    ):
        super().__init__(
            redis_url=redis_url,
            index_name=index_name,
            embedding_function = embedding_function,
            content_key = content_key,
            metadata_key = metadata_key,
            vector_key = vector_key
        )
        # The graph key used to store the graphs
        self.graph_key = graph_key
        # The program key used to store the programs
        self.program_key = program_key
        # RedisGraph client for the metagraph
        self.metagraph = Graph(self.graph_key+":metagraph", self.client)
        # RedisGraph client for the main graph program
        self.main = Graph(self.program_key+":main", self.client)
        # RedisGraph client for the playground (allowing to test programs in realtime)
        self.playground = Graph(self.program_key+":playground", self.client)

    def get_content(self, content_key:str) -> str:
        """Get content from Redis"""
        result = self.client.hget(content_key, self.content_key)
        return result.decode('utf-8')

    def get_content_metadata(self, content_key:str) -> Dict[Any, Any]:
        """Get content metadata from Redis"""
        result = self.client.hget(content_key, self.metadata_key)
        return json.load(result)

    def get_content_vector(self, content_key:str) -> np.array:
        """Get content vector from Redis"""
        result = self.client.hget(content_key, self.vector_key)
        return np.frombuffer(result)

    def set_content(self, content_key:str, text:str) -> bool:
        """Set the content entry"""
        return self.client.hset(content_key, self.content_key, text)

    def set_content_metadata(self, content_key:str, metadata:dict = {}) -> bool:
        """Set the metadata of the content entry"""
        return self.client.hset(content_key, self.metadata_key, json.dumps(metadata))

    def set_content_vector(self, content_key:str, content:str) -> dict:
        """Set the vector of the content entry"""
        embedding = self.embedding_function(content)
        vector_data = np.array(embedding, dtype=np.float32).tobytes(),
        return self.client.hset(content_key, self.vector_key, vector_data)

    def delete_content(self, content_key) -> bool:
        return self.client.delete(content_key)

    def redis_key(self, prefix: str) -> str:
        """Redis key schema for a given prefix."""
        return f"{prefix}:{uuid.uuid4().hex}"

    def redis_prefix(self, index_name: str) -> str:
        """Redis key prefix for a given index."""
        return f"doc:{index_name}"

    def clear(self):
        self.client.flushall()