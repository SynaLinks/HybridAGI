import abc
from typing import Any

class OutputParser():

    @abc.abstractmethod
    def parse(self, output: str) -> Any:
        pass