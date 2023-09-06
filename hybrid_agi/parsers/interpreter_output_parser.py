"""The Interpreter output parser. Copyright (C) 2023 SynaLinks. License: GPL-3.0"""
import re
from langchain.schema import BaseOutputParser

class InterpreterOutputParser(BaseOutputParser):
    """
    The Output Parser for the program interpreter
    """
    def parse(self, output: str) -> str:
        """Fix and validate the output"""
        output = output.replace("```\n```","```")
        match = re.search(r"\nAction|\nDecision", output)
        if match:
            return output[:match.start()]
        else:
            return output

    def get_format_instructions(self) -> str:
        """Returns the formating instructions."""
        instructions = ""
        return instructions
