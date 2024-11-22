import dspy
import copy
from .tool import Tool
from typing import Optional, Callable
from pydantic import BaseModel
from hybridagi.core.datatypes import (
    ToolInput,
    GraphProgramList,
    Document,
)
from hybridagi.memory import ProgramMemory
from hybridagi.core.pipeline import Pipeline
from hybridagi.output_parsers import PredictionOutputParser
from hybridagi.output_parsers import CypherOutputParser

class AddGraphProgramSignature(dspy.Signature):
    objective = dspy.InputField(desc = "The long-term objective (what you are doing)")
    context = dspy.InputField(desc = "The previous actions (what you have done)")
    purpose = dspy.InputField(desc = "The purpose of the action (what you have to do now)")
    prompt = dspy.InputField(desc = "The action specific instructions (How to do it)")
    name = dspy.OutputField(desc = "The name of the cypher file")
    document = dspy.OutputField(desc = "The plan to save into memory")

class AddGraphProgramTool(Tool):
    
    def __init__(
            self,
            program_memory: ProgramMemory,
            pipeline: Optional[Pipeline] = None,
            name = "AddGraphProgram",
            description: str = "Usefull to save new methodologies/plans into memory",
            lm: Optional[dspy.LM] = None,
        ):
        super().__init__(
            name = name,
            description = description,
            lm = lm,
            )
        self.program_memory = program_memory
        self.pipeline = pipeline
        self.predict = dspy.Predict(AddGraphProgramSignature)
        self.prediction_parser = PredictionOutputParser()
        
    def forward(self, tool_input: ToolInput) -> GraphProgramList:
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
            document = Document(text=pred.document)
            programs = self.pipeline(document)
            self.program_memory.update(programs)
            return programs
        else:
            raise NotImplementedError(f"{type(self).__name__} does not support disabling inference")