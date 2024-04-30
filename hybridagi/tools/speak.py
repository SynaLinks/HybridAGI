"""The speak tool. Copyright (C) 2024 SynaLinks. License: GPL-3.0"""

import copy
from typing import List, Optional, Callable
from colorama import Fore, Style
import dspy
from .base import BaseTool
from ..types.state import AgentState
from ..parsers.prediction import PredictionOutputParser

class SpeakSignature(dspy.Signature):
    """You will be given an objective, purpose and context
    Using the prompt to help you, you will infer the correct message to send to the user"""
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
        self.predict = dspy.Predict(SpeakSignature)
        self.simulated = simulated
        self.agent_state = agent_state
        self.speak_func = speak_func
        self.prediction_parser = PredictionOutputParser()

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
            pred = self.predict(
                objective = objective,
                context = context,
                purpose = purpose,
                prompt = prompt,
            )
            pred.message = self.prediction_parser.parse(
                pred.message,
                prefix = "Message:",
            )
            self.agent_state.chat_history.append(
                {"role": "AI", "message": pred.message}
            )
            if not self.simulated:
                self.speak(pred.message)
            return dspy.Prediction(
                message = pred.message
            )
        else:
            self.agent_state.chat_history.append(
                {"role": "AI", "message": prompt}
            )
            if not self.simulated:
                self.speak(prompt)
            return dspy.Prediction(
                message = prompt
            )

    def __deepcopy__(self, memo):
        cpy = (type)(self)(
            agent_state = self.agent_state,
            speak_func = self.speak_func,
            simulated = self.simulated,
        )
        cpy.predict = copy.deepcopy(self.predict)
        return cpy