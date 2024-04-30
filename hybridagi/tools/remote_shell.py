"""The remote shell tool. Copyright (C) 2024 SynaLinks. License: GPL-3.0"""

import requests
import shlex
import copy
import dspy
from .base import BaseTool
from ..parsers.prediction import PredictionOutputParser

class RemoteShellSignature(dspy.Signature):
    """You will be given an objective, purpose and context
    Using the prompt to help you, you will infer the correct unix shell command"""
    objective = dspy.InputField(desc = "The long-term objective (what you are doing)")
    context = dspy.InputField(desc = "The previous actions (what you have done)")
    purpose = dspy.InputField(desc = "The purpose of the action (what you have to do now)")
    prompt = dspy.InputField(desc = "The action specific instructions (How to do it)")
    unix_shell_command = dspy.OutputField(desc = "The unix shell command")

class RemoteShellTool(BaseTool):

    def __init__(
            self,
            sandbox_url: str,
            endpoint: str = "/cmdexec",
        ):
        super().__init__(name = "RemoteShell")
        self.predict = dspy.Predict(RemoteShellSignature)
        self.prediction_parser = PredictionOutputParser()
        self.sandbox_url = sandbox_url
        self.endpoint = endpoint

    def execute(self, command: str) -> str:
        payload = {"cmd": command}
        response = requests.post(self.sandbox_url+self.endpoint, json=payload)
        response.raise_for_status()
        return response.text.replace("\\n", "\n").strip("\"").strip()
    
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
            pred.unix_shell_command = self.prediction_parser.parse(
                pred.unix_shell_command.strip("`"),
                prefix = "Unix Shell Command:",
                stop = ["\n"],
            )
            observation = self.execute(pred.unix_shell_command)
            return dspy.Prediction(
                unix_shell_command = pred.unix_shell_command,
                observation = observation,
            )
        else:
            observation = self.execute(prompt)
            return dspy.Prediction(
                unix_shell_command = prompt,
                observation = observation,
            )