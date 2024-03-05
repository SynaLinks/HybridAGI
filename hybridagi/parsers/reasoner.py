"""The interpreter output parser. Copyright (C) 2023 SynaLinks. License: GPL-3.0"""

import re
from langchain.schema import BaseOutputParser

class ReasonerOutputParser(BaseOutputParser):
    """
    The Output Parser for the program interpreter
    """
    def parse(self, output: str) -> str:
        """Fix and validate the output"""
        output = output.replace("\n```\n```","```").strip()
        match = re.search(r"\nFinal Answer:", output)
        if match:
            output = output[match.end():]
        match = re.search(r"\nExplanation:|\nAnswer|\nAction|\nDecision|\nStart|\nEnd", output)
        if match:
            output = output[:match.start()]
        return output.strip()

    def get_format_instructions(self) -> str:
        """Returns the formating instructions."""
        instructions = ""
        return instructions
