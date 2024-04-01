"""The path output parser. Copyright (C) 2023 SynaLinks. License: GPL-3.0"""

from .base import BaseOutputParser

class PathOutputParser(BaseOutputParser):
    """
    The Output Parser for the paths
    """
    def parse(self, output:str) -> str:
        """Fix and validate the given path."""
        path = output.strip()
        path = path.replace("\\_", "_")
        path = path.strip("\"'")
        path = path.rstrip(",.;")
        if len(path) > 1:
            path = path.rstrip("/")
        return path