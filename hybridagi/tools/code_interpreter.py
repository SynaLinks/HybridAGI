"""The read file tool. Copyright (C) 2024 SynaLinks. License: GPL-3.0"""

import copy
import dspy
from typing import Optional
from .base import BaseTool
from ..utility.code_interpreter import CodeInterpreterUtility
from ..output_parsers.prediction import PredictionOutputParser

class CodeInterpreterSignature(dspy.Signature):
    """You will be given an objective, purpose and context
    Using the prompt to help you, you will infer the correct code"""
    objective = dspy.InputField(desc = "The long-term objective (what you are doing)")
    context = dspy.InputField(desc = "The previous actions (what you have done)")
    purpose = dspy.InputField(desc = "The purpose of the action (what you have to do now)")
    prompt = dspy.InputField(desc = "The action specific instructions (How to do it)")
    code = dspy.OutputField(desc = "The code to write")

# class CorrectCodeSignature(dspy.Signature):
#     """You will be given a code and error,
#     using the error to help you you will infer the corrected code"""
#     input_code = dspy.InputField(desc = "The code to correct")
#     error = dspy.InputField(desc = "The error encountered")
#     corrected_code = dspy.OutputField(desc = "The corrected code")

class CodeInterpreterTool(BaseTool):

    def __init__(
            self,
            code_interpreter: Optional[CodeInterpreterUtility] = None,
            preloaded_python_code: str = ""
        ):
        super().__init__(name = "CodeInterpreter")
        self.predict = dspy.Predict(CodeInterpreterSignature)
        # self.correct = dspy.Predict(CorrectCodeSignature)
        self.preloaded_python_code = preloaded_python_code
        if code_interpreter:
            self.code_interpreter = code_interpreter
            self.code_interpreter.reset()
        else:
            self.code_interpreter = CodeInterpreterUtility()
        if preloaded_python_code:
            self.code_interpreter.add_and_run(preloaded_python_code)
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
            pred = self.predict(
                objective = objective,
                context = context,
                purpose = purpose,
                prompt = prompt,
            )
            pred.code = pred.code.replace("\\n", "\n")
            pred.code = self.prediction_parser.parse(pred.code,
                prefix="\n\n```python\n",
                stop = ["\n```", "\n```\n\n"],
            )
            pred.code = self.prediction_parser.parse(pred.code,
                prefix="```python\n",
                stop = ["\n```", "\n```\n\n"],
            )
            result, plots, err = self.code_interpreter.add_and_run(pred.code)
            return dspy.Prediction(
                code = pred.code,
                observation = result,
            )
        else:
            result, plots, err = self.code_interpreter.add_and_run(prompt)
            return dspy.Prediction(
                code = prompt,
                observation = result,
            )

    def __deepcopy__(self, memo):
        cpy = (type)(self)(
            code_interpreter = self.code_interpreter,
            preloaded_python_code = self.preloaded_python_code
        )
        cpy.predict = copy.deepcopy(self.predict)
        # cpy.correct = copy.deepcopy(self.correct)
        return cpy
