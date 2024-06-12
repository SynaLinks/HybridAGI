"""The read program tool. Copyright (C) 2024 SynaLinks. License: GPL-3.0"""

import copy
import dspy
from .base import BaseTool
from typing import Optional
from ..hybridstores.program_memory.program_memory import ProgramMemory
from ..output_parsers.program_name import ProgramNameOutputParser

class ReadProgramSignature(dspy.Signature):
    """You will be given an objective, purpose and context
    Using the prompt to help you, you will infer the correct filename"""
    objective = dspy.InputField(desc = "The long-term objective (what you are doing)")
    context = dspy.InputField(desc = "The previous actions (what you have done)")
    purpose = dspy.InputField(desc = "The purpose of the action (what you have to do now)")
    prompt = dspy.InputField(desc = "The action specific instructions (How to do it)")
    filename = dspy.OutputField(desc = "The name of the program to read")

class ReadProgramTool(BaseTool):

    def __init__(
            self,
            program_memory: ProgramMemory,
            lm: Optional[dspy.LM] = None,
        ):
        super().__init__(name = "ReadProgram", lm = lm)
        self.predict = dspy.Predict(ReadProgramSignature)
        self.program_memory = program_memory
        self.parser = ProgramNameOutputParser()

    def read_program(self, name: str) -> str:
        try:
            program = self.program_memory.get_content(name)
            return program
        except Exception as err:
            return str(err)
    
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
            pred.filename = self.parser.parse(pred.filename)
            observation = self.read_program(pred.filename)
            return dspy.Prediction(
                filename = pred.filename,
                content = observation,
            )
        else:
            observation = self.read_program(prompt)
            return dspy.Prediction(
                filename = prompt,
                content = observation,
            )

    def __deepcopy__(self, memo):
        cpy = (type)(self)(
            program_memory = self.program_memory,
        )
        cpy.predict = copy.deepcopy(self.predict)
        return cpy