from .base import BaseOutputParser
from typing import List

class PredictionOutputParser(BaseOutputParser):
    """
    The output parser for predictions
    """

    def parse(self, output: str, prefix:str) -> str:
        first_occurence = output.find(prefix)
        if first_occurence >= 0:
            output[first_occurence+len(prefix):]
        ouput = output.strip()
        return output