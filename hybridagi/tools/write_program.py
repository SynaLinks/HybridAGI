"""The write file tool. Copyright (C) 2024 SynaLinks. License: GPL-3.0"""

import copy
import dspy
from .base import BaseTool
from ..hybridstores.program_memory.program_memory import ProgramMemory
from ..parsers.program_name import ProgramNameOutputParser
from ..parsers.cypher import CypherOutputParser
from ..utility.tester import TesterUtility

class WriteProgramSignature(dspy.Signature):
    """Infer the filename and content to write a cypher program into memory
    
    The content should have the following format:

    ```
    CREATE 
    ```
    """
    objective = dspy.InputField(desc = "The long-term objective (what you are doing)")
    context = dspy.InputField(desc = "The previous actions (what you have done)")
    purpose = dspy.InputField(desc = "The purpose of the action (what you have to do now)")
    prompt = dspy.InputField(desc = "The action specific instructions (How to do it)")
    filename = dspy.OutputField(desc = "The name of the cypher file (short and concise) to write without additional details")
    cypher_create_query = dspy.OutputField(desc = "The cypher query to write")

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
        self.program_tester = TesterUtility()

    def write_program(self, filename: str, content: str) -> str:
        try:
            program_name = self.program_name_parser.parse(filename)
            content = self.cypher_parser.parse(content)
            self.program_tester.verify_programs(
                [program_name],
                [content],
            )
            self.program_memory.add_texts(texts = [content], ids = [program_name])
            return "Successfully created"
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
            prediction = self.predict(
                objective = objective,
                context = context,
                purpose = purpose,
                prompt = prompt,
            )
            dspy.Suggest(
                len(filename) != 0,
                "The filename should not be empty"
            )
            dspy.Suggest(
                len(filename) < 100,
                "The filename should be short and consice"
            )
            observation = self.write_file(filename, prediction.cypher_create_query)
            return dspy.Prediction(
                filename = filename,
                content = prediction.content,
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