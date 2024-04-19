"""The program name output parser. Copyright (C) 2023 SynaLinks. License: GPL-3.0"""

import re
from .base import BaseOutputParser

class ProgramNameOutputParser(BaseOutputParser):
    """
    The Output Parser for program names
    """
    def parse(self, output:str) -> str:
        """Fix and validate the given Cypher query."""
        output = output.replace("\"", "")
        output = output.replace("\\_", "_")
        output = output.strip("\"'. \n")
        output = output.replace(".cypher", "")
        output = re.sub('(?!^)([A-Z]+)', r'_\1', output).lower()
        return output.strip()