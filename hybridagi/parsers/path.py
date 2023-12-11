"""The path output parser. Copyright (C) 2023 SynaLinks. License: GPL-3.0"""

from langchain.schema import BaseOutputParser

class PathOutputParser(BaseOutputParser):
    """
    The Output Parser for the paths
    """
    def parse(self, output:str) -> str:
        """Fix and validate the given Cypher query."""
        return self.fix_path(output)

    def get_format_instructions(self) -> str:
        """Returns the formating instructions"""
        instructions = "The output should be a unix-like path"
        return instructions

    def fix_path(self, path):
        path = path.replace('"', "")
        path = path.strip()
        if len(path) > 1:
            if path[len(path)-1] == "/":
                path = path[:len(path)-1]
        return path