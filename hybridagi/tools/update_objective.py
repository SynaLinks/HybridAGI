"""The update objective tool. Copyright (C) 2024 SynaLinks. License: GPL-3.0"""

import copy
import dspy
from .base import BaseTool
from typing import Optional, Callable
from ..types.state import AgentState
from ..parsers.prediction import PredictionOutputParser

class UpdateObjectiveSignature(dspy.Signature):
    """You will be given an objective, purpose and context
    Using the prompt to help you, you will infer the correct objective"""
    objective = dspy.InputField(desc = "The long-term objective (what you are doing)")
    context = dspy.InputField(desc = "The previous actions (what you have done)")
    purpose = dspy.InputField(desc = "The purpose of the action (what you have to do now)")
    prompt = dspy.InputField(desc = "The action specific instructions (How to do it)")
    new_objective = dspy.OutputField(desc = "The new objective")

class UpdateObjectiveTool(BaseTool):

    def __init__(
            self,
            agent_state: AgentState,
        ):
        super().__init__(name = "UpdateObjective")
        self.agent_state = agent_state
        self.predict = dspy.Predict(UpdateObjectiveSignature)
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
            pred = self.predict(
                context = context,
                objective = objective,
                purpose = purpose,
                prompt = prompt,
            )
            pred.new_objective = self.prediction_parser.parse(
                pred.new_objective,
                prefix="New Objective:"
            )
            pred.new_objective = self.prediction_parser.parse(
                pred.new_objective,
                prefix="Objective:"
            )
            self.agent_state.objective = pred.new_objective
            observation = "Successfully updated"
            return dspy.Prediction(
                new_objective = pred.new_objective,
                observation = observation,
            )
        else:
            self.agent_state.objective = prompt
            return dspy.Prediction(
                new_objective = prompt,
                observation = "Successfully updated",
            )

    def __deepcopy__(self, memo):
        cpy = (type)(self)(
            agent_state = self.agent_state,
        )
        cpy.predict = copy.deepcopy(self.predict)
        return cpy
