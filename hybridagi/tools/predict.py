import dspy
from .base import BaseTool
from typing import Optional

class PredictSignature(dspy.Signature):
    """Answer as best as possible according to the provided instructions"""
    trace = dspy.InputField(desc="Previous actions")
    objective = dspy.InputField(desc="Long-term objective")
    purpose = dspy.InputField(desc="Short-term purpose")
    prompt = dspy.InputField(desc="Task specific instructions")
    answer = dspy.OutputField(desc="Answer that follow the task specific instructions")

class PredictTool(BaseTool):

    def __init__(self):
        super().__init__(name = "Predict")
        self.predict = dspy.Predict(PredictSignature)
    
    def forward(
            self,
            trace: str,
            objective: str,
            purpose: str,
            prompt: str,
            disable_inference: bool = False,
            stop: Optional[str] = None,
        ) -> dspy.Prediction:
        if not disable_inference:
            pred = self.predict(
                objective = objective,
                purpose = purpose,
                trace = trace,
                prompt = prompt,
                stop = stop,
            )
            return dspy.Prediction(
                answer = pred.answer
            )
        else:
            return dspy.Prediction(
                answer = prompt
            )