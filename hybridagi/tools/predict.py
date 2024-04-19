"""The predict tool. Copyright (C) 2024 SynaLinks. License: GPL-3.0"""

import dspy
from .base import BaseTool
from ..parsers.prediction import PredictionOutputParser

class PredictSignature(dspy.Signature):
    """Infer the best answer according to the provided instructions"""
    objective = dspy.InputField(desc = "The long-term objective (what you are doing)")
    context = dspy.InputField(desc = "The previous actions (what you have done)")
    purpose = dspy.InputField(desc = "The purpose of the action (what you have to do now)")
    prompt = dspy.InputField(desc = "The action specific instructions (How to do it)")
    answer = dspy.OutputField(desc = "The right answer with the right format")

class PredictTool(BaseTool):

    def __init__(self):
        super().__init__(name = "Predict")
        self.predict = dspy.Predict(PredictSignature)
        self.prediction_parser = PredictionOutputParser()
    
    def forward(
            self,
            context: str,
            objective: str,
            purpose: str,
            prompt: str,
            disable_inference: bool = False,
        ) -> dspy.Prediction:
        """Method to perform DSPy forward prediction"""
        if not disable_inference:
            prediction = self.predict(
                objective = objective,
                context = context,
                purpose = purpose,
                prompt = prompt,
            )
            answer = self.prediction_parser.parse(prediction.answer, prefix = "Answer:")
            return dspy.Prediction(
                answer = answer
            )
        else:
            return dspy.Prediction(
                answer = prompt
            )