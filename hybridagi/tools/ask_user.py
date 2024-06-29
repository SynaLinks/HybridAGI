"""The ask user tool. Copyright (C) 2024 SynaLinks. License: GPL-3.0"""

import copy
from typing import List, Optional, Callable, Optional
import json
import dspy
from .base import BaseTool
from ..types.state import AgentState
from ..output_parsers.prediction import PredictionOutputParser

class AskUserSignature(dspy.Signature):
    """You will be given an objective, purpose and context
    Using the prompt to help you, you will infer the correct question"""
    objective = dspy.InputField(desc = "The long-term objective (what you are doing)")
    context = dspy.InputField(desc = "The previous actions (what you have done)")
    purpose = dspy.InputField(desc = "The purpose of the action (what you have to do now)")
    prompt = dspy.InputField(desc = "The action specific instructions (how to do it)")
    question = dspy.OutputField(desc = "The question to ask to the user")

class SimulateAnswerSignature(dspy.Signature):
    """Answer from the perspective of a real person, if you don't known imagine what a user with the given profile would answer"""
    objective = dspy.InputField(desc = "The long-term objective (what you are doing)")
    user_profile = dspy.InputField(desc = "The user profile")
    chat_history = dspy.InputField(desc = "The chat history")
    question = dspy.InputField(desc = "The question to assess")
    user_answer = dspy.OutputField(desc = "The answer from the perspective of a real person (only few words)")

class AskUserTool(BaseTool):

    def __init__(
            self,
            agent_state: AgentState,
            user_profile: str = "An average user",
            ask_user_func: Optional[Callable[[str], str]] = None,
            num_history: int = 50,
            simulated: bool = True,
            lm: Optional[dspy.LM] = None,
        ):
        super().__init__(name = "AskUser", lm = lm)
        self.predict = dspy.Predict(AskUserSignature)
        self.simulated = simulated
        self.simulate = dspy.Predict(SimulateAnswerSignature)
        self.agent_state = agent_state
        self.num_history = num_history
        self.ask_user_func = ask_user_func
        self.prediction_parser = PredictionOutputParser()

    def ask_user(self, question : str) -> str:
        if self.ask_user_func:
            return self.ask_user_func(question)
        else:
            raise ValueError(
                "You should specify a function to call to use `AskUser` outside simulation")

    def simulate_ask_user(self, question: str):
        chat_history = json.dumps(self.agent_state.chat_history[:-self.num_history], indent=2)
        pred = self.simulate(
            objective = self.agent_state.objective,
            chat_history = chat_history,
            question = question,
        )
        with dspy.context(lm=self.lm if self.lm is not None else dspy.settings.lm):
            pred.answer = self.prediction_parser.parse(
                pred.user_answer,
                prefix = "User Answer:",
            )
        return pred.answer

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
            with dspy.context(lm=self.lm if self.lm is not None else dspy.settings.lm):
                pred = self.predict(
                    objective = objective,
                    context = context,
                    purpose = purpose,
                    prompt = prompt,
                )
            pred.question = self.prediction_parser.parse(
                pred.question,
                prefix = "Question:",
            )
            self.agent_state.chat_history.append(
                {"role": "AI", "message": pred.question}
            )
            if self.simulated:
                answer = self.simulate_ask_user(pred.question)
            else:
                answer = self.ask_user(pred.question)
            self.agent_state.chat_history.append(
                {"role": "User", "message": answer}
            )
            return dspy.Prediction(
                question = pred.question,
                answer = answer,
            )
        else:
            self.agent_state.chat_history.append(
                {"role": "AI", "message": prompt}
            )
            if self.simulated:
                answer = self.simulate_ask_user(prompt)
            else:
                answer = self.ask_user(message)
            self.agent_state.chat_history.append(
                {"role": "User", "message": answer}
            )
            return dspy.Prediction(
                question = prompt,
                answer = answer,
            )

    def __deepcopy__(self, memo):
        cpy = (type)(self)(
            agent_state = self.agent_state,
            num_history = self.num_history,
            ask_user_func = self.ask_user_func,
            simulated = self.simulated,
            lm = self.lm,
        )
        cpy.predict = copy.deepcopy(self.predict)
        return cpy