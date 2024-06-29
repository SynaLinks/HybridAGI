"""The read file tool. Copyright (C) 2024 SynaLinks. License: GPL-3.0"""

import copy
import dspy
from typing import Optional
from .base import BaseTool
from ..types.state import AgentState
from ..utility.code_interpreter import CodeInterpreterUtility
from ..output_parsers.prediction import PredictionOutputParser

class CodeInterpreterSignature(dspy.Signature):
    """You will be given an objective, purpose and context
    Using the prompt to help you, you will infer the correct code
    
    Note: Never ask for user input and ensure that your last make sure the last line in your code evaluates to the correct value"""
    objective = dspy.InputField(desc = "The long-term objective (what you are doing)")
    context = dspy.InputField(desc = "The previous actions (what you have done)")
    purpose = dspy.InputField(desc = "The purpose of the action (what you have to do now)")
    prompt = dspy.InputField(desc = "The action specific instructions (How to do it)")
    code = dspy.OutputField(desc = "The code to write")

class CodeInterpreterTool(BaseTool):

    def __init__(
            self,
            code_interpreter: Optional[CodeInterpreterUtility] = None,
            lm: Optional[dspy.LM] = None,
        ):
        super().__init__(name = "CodeInterpreter", lm = lm)
        self.predict = dspy.Predict(CodeInterpreterSignature)
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
            code, output, err = self.code_interpreter.execute_code(pred.code)
            if not err:
                result = output
            else:
                result = err
            return dspy.Prediction(
                code = pred.code,
                observation = result,
            )
        else:
            code, output, err = self.code_interpreter.execute_code(prompt)
            if not err:
                result = output
            else:
                result = err
            return dspy.Prediction(
                code = prompt,
                observation = result,
            )

    def __deepcopy__(self, memo):
        cpy = (type)(self)(
            code_interpreter = self.code_interpreter,
            lm = self.lm,
        )
        cpy.predict = copy.deepcopy(self.predict)
        return cpy
        