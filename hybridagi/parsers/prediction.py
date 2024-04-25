import re
from .base import BaseOutputParser
from typing import List

class PredictionOutputParser(BaseOutputParser):
    """
    The output parser for predictions
    """

    def parse(self, output: str, prefix: str, stop: List[str] = []) -> str:
        first_occurence = output.find(prefix)
        if first_occurence >= 0:
            output = output[first_occurence+len(prefix):]
        for s in stop:
            first_occurence = output.find(s)
            if first_occurence >= 0:
                output = output[:first_occurence]
        output = output.strip()
        return output
