import abc
import dspy

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
        ) -> dspy.Prediction:
        pass