import dspy
from .tool import Tool
from typing import Optional, Callable
from hybridagi.core.datatypes import (
    ToolInput,
)
from hybridagi.output_parsers.prediction import PredictionOutputParser

class ChainOfThoughtSignature(dspy.Signature):
    objective = dspy.InputField(desc = "The long-term objective (what you are doing)")
    context = dspy.InputField(desc = "The previous actions (what you have done)")
    purpose = dspy.InputField(desc = "The purpose of the action (what you have to do now)")
    prompt = dspy.InputField(desc = "The action specific instructions (How to do it)")
    answer = dspy.OutputField(desc = "The correct answer")

class PredictOutput(dspy.Prediction):
    answer: str

class ChainOfThoughtTool(Tool):
    def __init__(
            self,
            lm: Optional[dspy.LM] = None,
        ):
        super().__init__(name = "Predict", lm = lm)
        self.predict = dspy.ChainOfThought(ChainOfThoughtSignature)
        self.prediction_parser = PredictionOutputParser()
        
    def forward(self, tool_input: ToolInput) -> SpeakOutput:
        if not tool_input.disable_inference:
            with dspy.context(lm=self.lm if self.lm is not None else dspy.settings.lm):
                pred = self.predict(
                    objective = tool_input.objective,
                    context = tool_input.context,
                    purpose = tool_input.purpose,
                    prompt = tool_input.prompt,
                )
            pred.answer = self.prediction_parser.parse(
                pred.message,
                prefix = "Answer:",
            )
            return PredictOutput(
                answer = pred.answer
            )
        else:
            return PredictOutput(
                answer = tool_input.prompt,
            )