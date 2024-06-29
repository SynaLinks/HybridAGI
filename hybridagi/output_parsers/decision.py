from .base import BaseOutputParser
from typing import List

class DecisionOutputParser(BaseOutputParser):
    """
    The output parser for decision making steps
    """

    def parse(self, output: str, options: List[str] = []) -> str:
        toks = output.split()
        if len(toks) > 0:
            token = toks[0].upper().strip(",.")
            if token in options:
                return token
        return output