import dspy
import copy
from .tool import Tool
from typing import Optional, Callable
from hybridagi.core.datatypes import (
    ToolInput,
)
from hybridagi.output_parsers import PredictionOutputParser

class ReadGraphProgramSignature(dspy.Signature):
    objective = dspy.InputField(desc = "The long-term objective (what you are doing)")
    context = dspy.InputField(desc = "The previous actions (what you have done)")
    purpose = dspy.InputField(desc = "The purpose of the action (what you have to do now)")
    prompt = dspy.InputField(desc = "The action specific instructions (How to do it)")
    name = dspy.OutputField(desc = "The routine name")

class ReadGraphProgramOutput(dspy.Prediction):
    name: str
    routine: GraphProgram
    
    def to_dict(self):
        return {"name": self.name, "routine": self.routine.to_dict()}

class ReadGraphProgramTool(Tool):
    def __init__(
            self,
            program_memory = program_memory,
            name: str = "ReadGraphProgram",
            lm: Optional[dspy.LM] = None,
        ):
        super().__init__(name = name, lm = lm)
        self.predict = dspy.Predict(PredictSignature)
        self.prediction_parser = PredictionOutputParser()
        self.program_memory = program_memory
        
    def read_graph_program(self, name: str):
        if self.program_memory.is_protected(name):
            raise ValueError("Cannot read a protected program")
        return self.program_memory.get(name).progs[0]
        
    def forward(self, tool_input: ToolInput) -> PredictOutput:
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
            pred.name = self.prediction_parser.parse(
                pred.name,
                prefix = "Answer:",
            )
            pred.name = pred.name.strip("\"")
            pred.name = pred.name.replace(".cypher", "")
            graph_program = self.read_graph_program(pred.name)
            return ReadGraphProgramOutput(
                name = pred.name,
                routine = graph_program,
            )
        else:
            graph_program = self.read_graph_program(tool_input.prompt)
            return ReadGraphProgramOutput(
                name = tool_input.prompt,
                routine = graph_program,
            )
            
    def __deepcopy__(self, memo):
        cpy = (type)(self)(
            program_memory = self.program_memory,
            name = self.name,
            lm = self.lm,
        )
        cpy.predict = copy.deepcopy(self.predict)
        return cpy