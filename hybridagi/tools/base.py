import abc
import dspy
from typing import Optional

class BaseTool(dspy.Module):

    def __init__(self, name: str):
        self.name = name

    @abc.abstractmethod
    def forward(
            self,
            trace: str,
            objective: str,
            purpose: str,
            prompt: str,
            disable_inference: bool = False,
            stop: Optional[str] = None,
        ) -> dspy.Prediction:
        pass