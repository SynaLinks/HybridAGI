"""The base output parser. Copyright (C) 2024 SynaLinks. License: GPL-3.0"""

import abc
from typing import Any

class BaseOutputParser():

    @abc.abstractmethod
    def parse(self, output: str) -> Any:
        pass