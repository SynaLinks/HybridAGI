"""The read file tool. Copyright (C) 2024 SynaLinks. License: GPL-3.0"""

import copy
import dspy
from .base import BaseTool
from typing import Optional
from ..hybridstores.filesystem.filesystem import FileSystem
from ..utility.reader import ReaderUtility
from ..output_parsers.path import PathOutputParser
from ..output_parsers.prediction import PredictionOutputParser
from ..types.state import AgentState

class ReadFileSignature(dspy.Signature):
    """You will be given an objective, purpose and context
    Using the prompt to help you, you will infer the correct filename"""
    objective = dspy.InputField(desc = "The long-term objective (what you are doing)")
    context = dspy.InputField(desc = "The previous actions (what you have done)")
    purpose = dspy.InputField(desc = "The purpose of the action (what you have to do now)")
    prompt = dspy.InputField(desc = "The action specific instructions (How to do it)")
    filename = dspy.OutputField(desc = "The name of the file to read")

class ReadFileTool(BaseTool):

    def __init__(
            self,
            filesystem: FileSystem,
            agent_state: AgentState,
            lm: Optional[dspy.LM] = None,
        ):
        super().__init__(name = "ReadFile", lm = lm)
        self.predict = dspy.Predict(ReadFileSignature)
        self.agent_state = agent_state
        self.filesystem = filesystem
        self.reader = ReaderUtility(filesystem=self.filesystem)
        self.prediction_parser = PredictionOutputParser()
        self.path_parser = PathOutputParser()

    def read_file(self, filename: str) -> str:
        try:
            filename = self.agent_state.context.eval_path(filename)
            return self.reader.read_document(filename)
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
            pred = self.predict(
                objective = objective,
                context = context,
                purpose = purpose,
                prompt = prompt,
            )
            pred.filename = self.prediction_parser.parse(
                pred.filename,
                prefix="Filename:",
                stop = ["\n"],
            )
            pred.filename = self.path_parser.parse(pred.filename)
            dspy.Suggest(
                len(pred.filename) < 250,
                "Filename must be short and consice"
            )
            observation = self.read_file(pred.filename)
            return dspy.Prediction(
                filename = pred.filename,
                content = observation,
            )
        else:
            observation = self.read_file(prompt)
            return dspy.Prediction(
                filename = prompt,
                content = observation,
            )

    def __deepcopy__(self, memo):
        cpy = (type)(self)(
            filesystem = self.filesystem,
            agent_state = self.agent_state,
        )
        cpy.predict = copy.deepcopy(self.predict)
        return cpy