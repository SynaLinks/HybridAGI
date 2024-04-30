"""The program of thought tool. Copyright (C) 2024 SynaLinks. License: GPL-3.0"""

import dspy
from .base import BaseTool
from ..parsers.prediction import PredictionOutputParser

class ProgramOfThoughtSignature(dspy.Signature):
    """You will be given an objective, purpose and context
    Using the prompt to help you, you will infer the correct answer"""
    objective = dspy.InputField(desc = "The long-term objective (what you are doing)")
    context = dspy.InputField(desc = "The previous actions (what you have done)")
    purpose = dspy.InputField(desc = "The purpose of the action (what you have to do now)")
    prompt = dspy.InputField(desc = "The action specific instructions (How to do it)")
    answer = dspy.OutputField(desc = "The answer")

class ProgramOfThoughtTool(BaseTool):

    def __init__(self):
        super().__init__(name = "ProgramOfThought")
        self.program_of_thought = dspy.ProgramOfThought(ProgramOfThoughtSignature)
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
            pred = self.program_of_thought(
                objective = objective,
                context = context,
                purpose = purpose,
                prompt = prompt,
            )
            pred.answer = self.prediction_parser.parse(pred.answer, prefix = "Answer:")
            return dspy.Prediction(
                answer = pred.answer
            )
        else:
            return dspy.Prediction(
                answer = prompt
            )