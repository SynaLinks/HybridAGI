"""The write file tool. Copyright (C) 2024 SynaLinks. License: GPL-3.0"""

import copy
import dspy
from .base import BaseTool
from ..hybridstores.program_memory.program_memory import ProgramMemory
from ..parsers.program_name import ProgramNameOutputParser
from ..parsers.cypher import CypherOutputParser
from ..parsers.prediction import PredictionOutputParser
from ..utility.tester import TesterUtility

class WriteProgramSignature(dspy.Signature):
    """You will be given an objective, purpose and context
    Using the prompt to help you, you will infer the correct filename and cypher query"""
    objective = dspy.InputField(desc = "The long-term objective (what you are doing)")
    context = dspy.InputField(desc = "The previous actions (what you have done)")
    purpose = dspy.InputField(desc = "The purpose of the action (what you have to do now)")
    prompt = dspy.InputField(desc = "The action specific instructions (How to do it)")
    filename = dspy.OutputField(desc="The name of the .cypher file (short and concise)")
    cypher_query = dspy.OutputField(desc = "The Cypher query to write into memory (make sure to comment non-Cypher lines)")

class WriteProgramTool(BaseTool):

    def __init__(
            self,
            program_memory: ProgramMemory,
        ):
        super().__init__(name = "WriteProgram")
        self.predict = dspy.Predict(WriteProgramSignature)
        self.program_memory = program_memory
        self.program_name_parser = ProgramNameOutputParser()
        self.cypher_parser = CypherOutputParser()
        self.prediction_parser = PredictionOutputParser()
        self.program_tester = TesterUtility(program_memory=program_memory)

    def write_program(self, filename: str, content: str) -> str:
        try:
            self.program_tester.verify_programs(
                [filename],
                [content],
            )
            self.program_memory.add_texts(texts = [content], ids = [filename])
            return "Successfully written"
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
            pred = self.predict(
                objective = objective,
                context = context,
                purpose = purpose,
                prompt = prompt,
            )
            pred.filename = self.prediction_parser.parse(pred.filename, prefix="File Name:", stop=["\n"])
            pred.filename = self.program_name_parser.parse(pred.filename)
            pred.cypher_query = self.prediction_parser.parse(pred.cypher_query, prefix="\n```cypher", stop=["\n```\n\n"])
            pred.cypher_query = self.cypher_parser.parse(pred.cypher_query)
            dspy.Suggest(
                len(pred.filename) != 0,
                "Filename should not be empty"
            )
            dspy.Suggest(
                len(pred.filename) < 250,
                "Filename should be short and consice"
            )
            observation = self.write_program(pred.filename, pred.cypher_query)
            return dspy.Prediction(
                filename = pred.filename,
                content = pred.cypher_query,
                observation = observation,
            )
        else:
            raise NotImplementedError("Disabling inference for WriteProgram not supported")

    def __deepcopy__(self, memo):
        cpy = (type)(self)(
            program_memory = self.program_memory,
        )
        cpy.predict = copy.deepcopy(self.predict)
        return cpy