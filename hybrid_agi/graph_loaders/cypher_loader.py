"""The Cypher graph loader. Copyright (C) 2023 SynaLinks. License: GPLv3"""

import uuid
import redis
from redisgraph import Graph

def _redis_key(prefix: str) -> str:
    """Redis key schema for a given prefix."""
    return f"{prefix}:{uuid.uuid4().hex}"

class CypherLoader(BaseGraphLoader):
    """Class to load .cypher files"""
    client: redis.Redis
    filepath: str
    graph_key: str = "graph"

    def load() -> Graph:
        """Method to load file"""
        if not filepath.endswith(".cypher"):
            raise ValueError("Cypher graph loader can only process .cypher files")
        f = open(self.filepath)
        file_content = f.read()
        graph = Graph(_redis_prefix(self.graph_key), self.client)
        graph.query(file_content)
        return graph