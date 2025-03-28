import dspy
import copy
from .tool import Tool
from typing import Optional, Callable
from hybridagi.core.datatypes import (
    ToolInput,
)
from hybridagi.output_parsers import PredictionOutputParser

class PredictSignature(dspy.Signature):
    objective = dspy.InputField(desc = "The long-term objective (what you are doing)")
    context = dspy.InputField(desc = "The previous actions (what you have done)")
    purpose = dspy.InputField(desc = "The purpose of the action (what you have to do now)")
    prompt = dspy.InputField(desc = "The action specific instructions (How to do it)")
    answer = dspy.OutputField(desc = "The correct answer")

class PredictOutput(dspy.Prediction):
    answer: str
    
    def to_dict(self):
        return {"answer": self.answer}

class PredictTool(Tool):
    def __init__(
            self,
            name: str = "Predict",
            description: str = "Usefull to ak yourself a question, summarize topics, elaborate on a subject or write texts",
            lm: Optional[dspy.LM] = None,
        ):
        super().__init__(
            name = name,
            description = description,
            lm = lm,
        )
        self.predict = dspy.Predict(PredictSignature)
        self.prediction_parser = PredictionOutputParser()
        
    def forward(self, tool_input: ToolInput) -> PredictOutput:
        if not isinstance(tool_input, ToolInput):
            raise ValueError(f"{type(self).__name__} input must be a ToolInput")
        if not tool_input.disable_inference:
            with dspy.context(lm=self.lm if self.lm is not None else dspy.settings.lm):
                pred = self.predict(
                    objective = tool_input.objective,
                    context = tool_input.context,
                    purpose = tool_input.purpose,
                    prompt = tool_input.prompt,
                )
            pred.answer = self.prediction_parser.parse(
                pred.answer,
                prefix = "Answer:",
            )
            pred.answer = pred.answer.strip("\"")
            return PredictOutput(
                answer = pred.answer
            )
        else:
            return PredictOutput(
                answer = tool_input.prompt,
            )
            
    def __deepcopy__(self, memo):
        cpy = (type)(self)(
            name = self.name,
            lm = self.lm,
        )
        cpy.predict = copy.deepcopy(self.predict)
        return cpy