import dspy
import copy
import re
from .tool import Tool
from typing import Optional, Callable
from hybridagi.memory import ProgramMemory
from hybridagi.core.datatypes import (
    ToolInput,
    AgentState,
)
from hybridagi.output_parsers import PredictionOutputParser

class CallGraphProgramSignature(dspy.Signature):
    objective = dspy.InputField(desc = "The long-term objective (what you are doing)")
    context = dspy.InputField(desc = "The previous actions (what you have done)")
    purpose = dspy.InputField(desc = "The purpose of the action (what you have to do now)")
    prompt = dspy.InputField(desc = "The action specific instructions (How to do it)")
    selected_name = dspy.OutputField(desc = "The most appropriate routine name")

class CallGraphProgramOutput(dspy.Prediction):
    name: str
    observation: str
    
    def to_dict(self):
        return {"name": self.name, "observation": self.observation}

class CallGraphProgramTool(Tool):
    def __init__(
            self,
            agent_state: AgentState,
            program_memory: ProgramMemory,
            name: str = "CallGraphProgram",
            lm: Optional[dspy.LM] = None,
        ):
        super().__init__(name = name, lm = lm)
        self.predict = dspy.Predict(CallGraphProgramSignature)
        self.prediction_parser = PredictionOutputParser()
        self.agent_state = agent_state
        self.program_memory = program_memory
        
    def call_program(self, program_name: str) -> str:
        if not self.program_memory.exist(program_name):
            return f"Error occured: Program {program_name} does not exist"
        if self.program_memory.is_protected(program_name):
            return "Error occured: Trying to call a protected program"
        current_step = self.agent_state.get_current_step()
        next_step = self.agent_state.get_current_program().get_next_step(current_step.id)
        self.agent_state.set_current_step(next_step)
        called_program = self.program_memory.get(program_name).progs[0]
        self.agent_state.call_program(called_program)
        return "Successfully called"
        
    def forward(self, tool_input: ToolInput) -> CallGraphProgramOutput:
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
            pred.selected_name = self.prediction_parser.parse(
                pred.selected_name,
                prefix = "Name:",
                stop = [" "],
            )
            pred.selected_name = pred.selected_name.strip("\"")
            pred.selected_name = pred.selected_name.replace(".cypher", "")
            pred.selected_name = re.sub('(?<!^)(?=[A-Z])', '_', pred.selected_name).lower()
            observation = self.call_program(pred.selected_name)
            return CallGraphProgramOutput(
                name = pred.selected_name,
                observation = observation,
            )
        else:
            observation = self.call_program(tool_input.prompt)
            return CallGraphProgramOutput(
                name = tool_input.prompt,
                observation = observation
            )
            
    def __deepcopy__(self, memo):
        cpy = (type)(self)(
            program_memory = self.program_memory,
            agent_state = self.agent_state,
            name = self.name,
            lm = self.lm,
        )
        cpy.predict = copy.deepcopy(self.predict)
        return cpy