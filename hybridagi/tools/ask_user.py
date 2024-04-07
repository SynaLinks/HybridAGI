"""The ask user tool. Copyright (C) 2024 SynaLinks. License: GPL-3.0"""

from typing import List
import json
import dspy
from .base import BaseTool

class AskUserSignature(dspy.Signature):
    """Infer the question to ask to the user"""
    objective = dspy.InputField(desc = "The long-term objective (what you are doing)")
    context = dspy.InputField(desc = "The previous actions (what you have done)")
    purpose = dspy.InputField(desc = "The purpose of the action (what you have to do now)")
    prompt = dspy.InputField(desc = "The action specific instructions (how to do it)")
    question = dspy.OutputField(desc = "The question to ask to the user")

class SimulateAnswerSignature(dspy.Signature):
    """Answer like a human user, if you don't known imagine what an average user would answer"""
    objective = dspy.InputField(desc = "The long-term objective (what you are doing)")
    chat_history = dspy.InputField(desc = "The chat history")
    question = dspy.InputField(desc = "The question to assess")
    answer = dspy.OutputField(desc = "The answer to the assessed question")

class AskUserTool(BaseTool):

    def __init__(
            self,
            chat_history: List[dict],
            num_history: int = 50,
            simulated: bool = True,
        ):
        super().__init__(name = "AskUser")
        self.predict = dspy.Predict(PredictSignature)
        self.simulated = simulated
        self.simulate = dspy.Predict(SimulateAnswerSignature)
        self.chat_history = chat_history
        self.num_history = num_history

    def ask_user(self, question : str) -> str:
        raise NotImplementedError("Not implemented yet")

    def simulate_ask_user(self, question: str):
        chat_history = json.dumps(self.chat_history[:-self.num_history], indent=2)
        simulation = self.simulate(
            objective = objective,
            chat_history = chat_history,
            question = question,
        )
        answer = simulation.answer
        return answer

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
            question = prediction.question
            self.chat_history.append(
                {"role": "AI", "message": question}
            )
            if self.simulated:
                answer = self.simulate_ask_user(question)
            else:
                answer = self.ask_user(question)
            self.chat_history.append(
                {"role": "User", "message": answer}
            )
            return dspy.Prediction(
                question = question,
                answer = answer,
            )
        else:
            self.chat_history.append(
                {"role": "AI", "message": prompt}
            )
            if self.simulated:
                answer = self.simulate_ask_user(question)
            else:
                answer = self.ask_user(message)
            self.chat_history.append(
                {"role": "User", "message": answer}
            )
            return dspy.Prediction(
                question = prompt,
                answer = answer,
            )