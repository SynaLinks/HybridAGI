"""The path output parser. Copyright (C) 2023 SynaLinks. License: GPL-3.0"""

from langchain.schema import BaseOutputParser

class PathOutputParser(BaseOutputParser):
    """
    The Output Parser for the paths
    """
    def parse(self, output:str) -> str:
        """Fix and validate the given path."""
        return self.fix_path(output)

    def get_format_instructions(self) -> str:
        """Returns the formating instructions"""
        instructions = "The output should be a unix-like path"
        return instructions

    def fix_path(self, path):
        path = path.strip()
        path = path.replace("\_", "_")
        path = path.strip("\"'")
        path = path.rstrip(",.;")
        if len(path) > 1:
            path = path.rstrip("/")
        return path