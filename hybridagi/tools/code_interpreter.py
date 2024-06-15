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

class CodeInterpreterTool(BaseTool):

    def __init__(
            self,
            code_interpreter: Optional[CodeInterpreterUtility] = None,
            preloaded_python_code: str = "",
            lm: Optional[dspy.LM] = None,
        ):
        super().__init__(name = "CodeInterpreter", lm = lm)
        self.predict = dspy.Predict(CodeInterpreterSignature)
        # self.correct = dspy.Predict(CorrectCodeSignature)
        self.preloaded_python_code = preloaded_python_code
        if code_interpreter:
            self.code_interpreter = code_interpreter
        else:
            self.code_interpreter = CodeInterpreterUtility()
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
            with dspy.context(lm=self.lm if self.lm is not None else dspy.settings.lm):
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
            preloaded_python_code = self.preloaded_python_code,
            lm = self.lm,
        )
        cpy.predict = copy.deepcopy(self.predict)
        return cpy
