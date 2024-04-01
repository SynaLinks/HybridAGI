from .base import BaseOutputParser
from typing import List

class DecisionOutputParser(BaseOutputParser):
    """
    The output parser for decision making steps
    """

    def parse(self, output: str, options: List[str] = []) -> str:
        for opt in options:
            if output.find("<"+opt+">"):
                return opt
        return output