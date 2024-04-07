"""The speak tool. Copyright (C) 2024 SynaLinks. License: GPL-3.0"""

from typing import List
from colorama import Fore, Style
import dspy
from .base import BaseTool

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
            chat_history: List[dict],
            simulated: bool = True,
        ):
        super().__init__(name = "Speak")
        self.predict = dspy.Predict(PredictSignature)
        self.simulated = simulated
        if self.simulated and chat_history is None:
            raise ValueError("Chat history required to simulate 'Speak' tool")
        self.chat_history = chat_history

    def speak(self, message: str):
        raise NotImplementedError("Not implemented yet")

    def simulate_speak(self, message: str):
        pass

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
            self.chat_history.append(
                {"role": "AI", "message": message}
            )
            if self.simulated:
                self.simulate_speak(message)
            else:
                self.speak(message)
            return dspy.Prediction(
                message = message
            )
        else:
            self.chat_history.append(
                {"role": "AI", "message": message}
            )
            if self.simulated:
                self.simulate_speak(message)
            else:
                self.speak(message)
            return dspy.Prediction(
                message = prompt
            )