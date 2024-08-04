from abc import abstractmethod
from typing import Any

class OutputParser():
    """
    The output parser base class
    """

    @abstractmethod
    def parse(self, output: str) -> Any:
        pass