"""The read user profile tool. Copyright (C) 2024 SynaLinks. License: GPL-3.0"""

import copy
import dspy
from .base import BaseTool
from typing import Optional, Callable
from ..types.state import AgentState

class ReadUserProfileTool(BaseTool):

    def __init__(
            self,
            agent_state: AgentState,
        ):
        super().__init__(name = "ReadUserProfile")
        self.agent_state = agent_state
        
    def forward(
            self,
            context: str,
            objective: str,
            purpose: str,
            prompt: str,
            disable_inference: bool = False,
        ) -> dspy.Prediction:
        """Method to perform DSPy forward prediction"""
        return dspy.Prediction(
            user_profile = self.agent_state.user_profile,
        )

    def __deepcopy__(self, memo):
        cpy = (type)(self)(
            agent_state = self.agent_state,
        )
        return cpy
