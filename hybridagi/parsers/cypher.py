"""The Cypher output parser. Copyright (C) 2023 SynaLinks. License: GPL-3.0"""

from .base import BaseOutputParser

class CypherOutputParser(BaseOutputParser):
    """
    The output parser for RedisGraph Cypher queries
    """

    def parse(self, output:str) -> str:
        """Fix and validate the given Cypher query."""
        output = output.strip()
        output = output.strip("\"'`")
        output = output.rstrip(".,;")
        return output