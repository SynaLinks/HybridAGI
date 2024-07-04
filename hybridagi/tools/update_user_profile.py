"""The update user profile tool. Copyright (C) 2024 SynaLinks. License: GPL-3.0"""

import copy
import dspy
from .base import BaseTool
from typing import Optional, Callable
from ..types.state import AgentState
from ..output_parsers.prediction import PredictionOutputParser

class UpdateUserProfileSignature(dspy.Signature):
    """You will be given an objective, purpose and context
    Using the prompt to help you, you will infer the correct user profile
    
    Note: Never give an apology or explain what you are doing."""
    objective = dspy.InputField(desc = "The long-term objective (what you are doing)")
    context = dspy.InputField(desc = "The previous actions (what you have done)")
    purpose = dspy.InputField(desc = "The purpose of the action (what you have to do now)")
    prompt = dspy.InputField(desc = "The action specific instructions (How to do it)")
    user_profile = dspy.OutputField(desc = "The user profile")

class UpdateUserProfileTool(BaseTool):

    def __init__(
            self,
            agent_state: AgentState,
            lm: Optional[dspy.LM] = None,
        ):
        super().__init__(name = "UpdateUserProfile")
        self.agent_state = agent_state
        self.prediction_parser = PredictionOutputParser()
        self.predict = dspy.Predictor(UpdateUserProfileSignature)

    def update_user_profile(self, user_profile: str):
        self.agent_state.user_profile = user_profile
        
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
            pred.user_profile = self.prediction_parser(
                pred.user_profile,
                prefix="User Profile:",
            )
            self.update_user_profile(pred.user_profile)
            return dspy.Prediction(
                user_profile = pred.user_profile,
                observation = "Successfully updated",
            )
        else:
            self.update_user_profile(prompt)
            return dspy.Prediction(
                user_profile = prompt,
                observation = "Successfully updated",
            )

    def __deepcopy__(self, memo):
        cpy = (type)(self)(
            agent_state = self.agent_state,
            lm = self.lm,
        )
        return cpy
