from abc import ABC, abstractmethod
import dspy
import copy
from hybridagi.core.datatypes import ToolInput
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
    def forward(self, tool_input: ToolInput) -> dspy.Prediction:
        if not isinstance(tool_input, ToolInput):
            raise ValueError(f"{type(self).__name__} input must be a ToolInput")
        raise NotImplementedError(
            f"Tool {type(self).__name__} is missing the required 'forward' method."
        )