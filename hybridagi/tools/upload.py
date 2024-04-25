"""The upload tool. Copyright (C) 2024 SynaLinks. License: GPL-3.0"""

import os
import copy
import dspy
from .base import BaseTool
from ..hybridstores.filesystem.filesystem import FileSystem
from ..utility.archiver import ArchiverUtility
from ..parsers.path import PathOutputParser
from ..types.state import AgentState

class UploadSignature(dspy.Signature):
    """You will be given an objective, purpose and context
    Using the prompt to help you, you will infer the correct filename"""
    objective = dspy.InputField(desc = "The long-term objective (what you are doing)")
    context = dspy.InputField(desc = "The previous actions (what you have done)")
    purpose = dspy.InputField(desc = "The purpose of the action (what you have to do now)")
    prompt = dspy.InputField(desc = "The action specific instructions (How to do it)")
    filename = dspy.OutputField(desc = "The name of the file or folder to upload to the user")

class UploadTool(BaseTool):

    def __init__(
            self,
            filesystem: FileSystem,
            agent_state: AgentState,
            downloads_directory: str = "",
        ):
        super().__init__(name = "Upload")
        self.predict = dspy.Predict(UploadSignature)
        self.agent_state = agent_state
        self.filesystem = filesystem
        downloads_directory = downloads_directory if downloads_directory else os.getcwd()
        self.reader = ArchiverUtility(
            filesystem=self.filesystem,
            downloads_directory=downloads_directory,
        )
        self.path_parser = PathOutputParser()

    def upload(self, filename: str) -> str:
        try:
            return self.archiver.upload(filename)
        except Exception as err:
            return str(err)
    
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
            filename = self.prediction_parser.parse(
                prediction.filename,
                prefix="Filename:",
            )
            filename = self.path_parser.parse(filename)
            filename = self.agent_state.context.eval_path(filename)
            observation = self.upload(filename)
            return dspy.Prediction(
                filename = filename,
                content = observation,
            )
        else:
            observation = self.upload(prompt)
            return dspy.Prediction(
                filename = prompt,
                content = observation,
            )

    def __deepcopy__(self, memo):
        cpy = (type)(self)(
            filesystem = self.filesystem,
            agent_state = self.agent_state,
            downloads_directory = self.downloads_directory,
        )
        cpy.predict = copy.deepcopy(self.predict)
        return cpy