"""The revert trace tool. Copyright (C) 2024 SynaLinks. License: GPL-3.0"""

import copy
import dspy
from .base import BaseTool
from typing import Optional, Callable
from ..types.state import AgentState
from pydantic import BaseModel

class Integer(BaseModel):
    integer: int

class RevertTraceSignature(dspy.Signature):
    """You will be given an objective, purpose and context
    Using the prompt to help you, you will infer the correct number of steps to revert"""
    objective = dspy.InputField(desc = "The long-term objective (what you are doing)")
    context = dspy.InputField(desc = "The previous actions (what you have done)")
    purpose = dspy.InputField(desc = "The purpose of the action (what you have to do now)")
    prompt = dspy.InputField(desc = "The action specific instructions (How to do it)")
    number: Integer = dspy.OutputField(desc = "The number of steps to revert")

class RevertTraceTool(BaseTool):

    def __init__(
            self,
            agent_state: AgentState,
        ):
        super().__init__(name = "RevertTrace")
        self.agent_state = agent_state
        self.predict = dspy.TypedPredictor(RevertTraceSignature)

    def revert_trace(self, k: int):
        self.agent_state.program_trace = self.agent_state.program_trace[:len(self.agent_state.program_trace)-k]
        
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
            nb = pred.number.integer
            self.revert_trace(nb)
            return None
        else:
            return None

    def __deepcopy__(self, memo):
        cpy = (type)(self)(
            agent_state = self.agent_state,
        )
        return cpy
