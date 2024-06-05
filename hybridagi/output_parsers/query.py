"""The query output parser. Copyright (C) 2023 SynaLinks. License: GPL-3.0"""

from .base import BaseOutputParser

class QueryOutputParser(BaseOutputParser):
    """
    The Output Parser for search queries
    """
    def parse(self, output:str) -> str:
        """Fix the given query"""
        return output.replace("\"", "").strip()