from abc import ABC, abstractmethod
import dspy
import copy
from typing import Optional, Union, Callable, Dict, Any
from dspy.signatures.signature import ensure_signature

class Tool(dspy.Module):

    def __init__(
            self,
            name: str,
            lm: Optional[dspy.LM] = None,
        ):
        self.name = name
        self.lm = lm

    @abstractmethod
    def forward(self, **kwargs) -> dspy.Prediction:
        pass