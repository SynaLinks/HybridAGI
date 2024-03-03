"""The program name output parser. Copyright (C) 2023 SynaLinks. License: GPL-3.0"""
import re
from langchain.schema import BaseOutputParser

class ProgramNameOutputParser(BaseOutputParser):
    """
    The Output Parser for program names
    """
    def parse(self, output:str) -> str:
        """Fix and validate the given Cypher query."""
        output = output.strip("\"'. \n")
        output = output.replace("\_", "_")
        output = output.replace(".cypher", "")
        output = re.sub('(?!^)([A-Z]+)', r'_\1', output).lower()
        return output.strip()

    def get_format_instructions(self) -> str:
        """Returns the formating instructions"""
        instructions = "The output should be the program name in snake case"
        return instructions