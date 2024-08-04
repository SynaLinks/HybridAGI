import dspy
from .tool import Tool
from typing import Optional, Callable
from hybridagi.core.datatypes import (
    ToolInput,
)
from hybridagi.output_parsers import PredictionOutputParser

class WriteGraphProgramSignature(dspy.Signature):
    objective = dspy.InputField(desc = "The long-term objective (what you are doing)")
    context = dspy.InputField(desc = "The previous actions (what you have done)")
    purpose = dspy.InputField(desc = "The purpose of the action (what you have to do now)")
    prompt = dspy.InputField(desc = "The action specific instructions (How to do it)")
    name = dspy.OutputField(desc = "The routine name")
    cypher_workflow = dspy.OutputField(desc = "The cypher workflow")

class WriteGraphProgramOutput(dspy.Prediction):
    name: str
    routine: GraphProgram
    observation: str
    
    def to_dict(self):
        return {"name": self.name, "routine": self.routine.to_dict(), "observation": self.observation}

class ReadGraphProgramTool(Tool):
    def __init__(
            self,
            program_memory = program_memory,
            name: str = "WriteGraphProgram",
            pipeline: Optional[Pipeline] = None,
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