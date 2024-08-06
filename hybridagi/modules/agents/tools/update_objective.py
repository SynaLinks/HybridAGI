import dspy
import copy
from .tool import Tool
from typing import Optional, Callable
from hybridagi.core.datatypes import (
    ToolInput,
    AgentState,
)
from hybridagi.output_parsers import PredictionOutputParser

class UpdateObjectiveSignature(dspy.Signature):
    objective = dspy.InputField(desc = "The long-term objective (what you are doing)")
    context = dspy.InputField(desc = "The previous actions (what you have done)")
    purpose = dspy.InputField(desc = "The purpose of the action (what you have to do now)")
    prompt = dspy.InputField(desc = "The action specific instructions (How to do it)")
    new_objective = dspy.OutputField(desc = "The new objective")

class UpdateObjectiveOutput(dspy.Prediction):
    new_objective: str
    
    def to_dict(self):
        return {"new_objective": self.new_objective}

class UpdateObjectiveTool(Tool):
    def __init__(
            self,
            agent_state: AgentState,
            name: str = "UpdateObjective",
            lm: Optional[dspy.LM] = None,
        ):
        super().__init__(name = name, lm = lm)
        self.predict = dspy.Predict(UpdateObjectiveSignature)
        self.prediction_parser = PredictionOutputParser()
        self.agent_state = agent_state
        
    def forward(self, tool_input: ToolInput) -> UpdateObjectiveOutput:
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
            pred.new_objective = self.prediction_parser.parse(
                pred.new_objective,
                prefix = "Objective:",
            )
            pred.new_objective = pred.new_objective.strip("\"")
            self.agent_state.objective.query = pred.new_objective
            return UpdateObjectiveOutput(
                new_objective = pred.new_objective,
            )
        else:
            self.agent_state.objective.query = tool_input.prompt
            return UpdateObjectiveOutput(
                new_objective = tool_input.prompt,
            )
            
    def __deepcopy__(self, memo):
        cpy = (type)(self)(
            agent_state = self.agent_state,
            name = self.name,
            lm = self.lm,
        )
        cpy.predict = copy.deepcopy(self.predict)
        return cpy