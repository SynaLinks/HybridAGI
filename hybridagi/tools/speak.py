"""The speak tool. Copyright (C) 2024 SynaLinks. License: GPL-3.0"""

from typing import List, Optional, Callable
from colorama import Fore, Style
import dspy
from .base import BaseTool
from ..types.state import AgentState

class SpeakSignature(dspy.Signature):
    """Infer what you want to say to the user"""
    objective = dspy.InputField(desc = "The long-term objective (what you are doing)")
    context = dspy.InputField(desc = "The previous actions (what you have done)")
    purpose = dspy.InputField(desc = "The purpose of the action (what you have to do now)")
    prompt = dspy.InputField(desc = "The action specific instructions (How to do it)")
    message = dspy.OutputField(desc = "The message to send to the user")

class SpeakTool(BaseTool):

    def __init__(
            self,
            agent_state: AgentState,
            speak_func: Optional[Callable[[str], None]] = None,
            simulated: bool = True,
        ):
        super().__init__(name = "Speak")
        self.predict = dspy.Predict(PredictSignature)
        self.simulated = simulated
        self.agent_state = agent_state
        self.speak_func = speak_func

    def speak(self, message: str):
        if self.speak_func:
            return self.speak_func(message)
        else:
            raise ValueError(
                "You should specify a function to call to use `Speak` outside simulation"
            )

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
            message = message.strip()
            self.agent_state.chat_history.append(
                {"role": "AI", "message": message}
            )
            if not self.simulated:
                self.speak(message)
            return dspy.Prediction(
                message = message
            )
        else:
            self.agent_state.chat_history.append(
                {"role": "AI", "message": message}
            )
            if not self.simulated:
                self.speak(message)
            return dspy.Prediction(
                message = prompt
            )