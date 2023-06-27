"""The Cypher graph loader. Copyright (C) 2023 SynaLinks. License: GPLv3"""

import uuid
from redisgraph import Graph
from hybrid_agi.graph_loaders.base import BaseGraphLoader

def _redis_key(prefix: str) -> str:
    """Redis key schema for a given prefix."""
    return f"{prefix}:{uuid.uuid4().hex}"

class CypherGraphLoader(BaseGraphLoader):
    """Class to load .cypher files"""

    def load(self, filepath: str, index: str = "") -> Graph:
        """Method to load file"""
        if not filepath.endswith(".cypher"):
            raise ValueError("Cypher graph loader can only process .cypher files")
        f = open(filepath)
        file_content = f.read()
        index = _redis_prefix(self.graph_key) if not index else index
        graph = Graph(index, self.client)
        graph.query(file_content)
        return graph