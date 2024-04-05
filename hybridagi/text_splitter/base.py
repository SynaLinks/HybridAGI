"""The base text splitter. Copyright (C) 2024 SynaLinks. License: GPL-3.0"""

import abc
from typing import List

class BaseTextSplitter():

    @abc.abstractmethod
    def split_text(self, text: str) -> List[str]:
        pass
