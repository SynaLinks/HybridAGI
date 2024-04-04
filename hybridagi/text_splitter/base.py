import abc
from typing import List

class BaseTextSplitter():

    @abc.abstractmethod
    def split_text(self, text: str) -> List[str]:
        pass
