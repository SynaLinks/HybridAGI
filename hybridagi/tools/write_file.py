"""The write file tool. Copyright (C) 2024 SynaLinks. License: GPL-3.0"""

import copy
import dspy
from .base import BaseTool
from ..hybridstores.filesystem.filesystem import FileSystem
from ..output_parsers.path import PathOutputParser
from ..output_parsers.prediction import PredictionOutputParser
from ..types.state import AgentState

class WriteFileSignature(dspy.Signature):
    """You will be given an objective, purpose and context
    Using the prompt to help you, you will infer the correct filename and content"""
    objective = dspy.InputField(desc = "The long-term objective (what you are doing)")
    context = dspy.InputField(desc = "The previous actions (what you have done)")
    purpose = dspy.InputField(desc = "The purpose of the action (what you have to do now)")
    prompt = dspy.InputField(desc = "The action specific instructions (How to do it)")
    filename = dspy.OutputField(desc = "The name of the file (short and concise)")
    content = dspy.OutputField(desc = "The content to write")

class WriteFileTool(BaseTool):

    def __init__(
            self,
            filesystem: FileSystem,
            agent_state: AgentState,
        ):
        super().__init__(name = "WriteFile")
        self.predict = dspy.Predict(WriteFileSignature)
        self.agent_state = agent_state
        self.filesystem = filesystem
        self.path_parser = PathOutputParser()
        self.prediction_parser = PredictionOutputParser()

    def write_file(self, filename: str, content: str) -> str:
        try:
            if self.filesystem.is_folder(filename):
                return "Error: Cannot override a directory"
            filename = self.agent_state.context.eval_path(filename)
            metadata = {}
            metadata["filename"] = filename
            self.filesystem.add_texts(
                texts = [content],
                ids = [filename],
                metadatas = [metadata],
            )
            return "Successfully written"
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
            pred.filename = self.prediction_parser.parse(pred.filename, prefix="Filename:", stop=["\n"])
            pred.filename = self.path_parser.parse(pred.filename)
            pred.content = self.prediction_parser.parse(pred.content, prefix="Content:")
            pred.content = self.prediction_parser.parse(pred.content, prefix="\n\n```\n", stop=["\n```\n\n"])
            dspy.Suggest(
                len(pred.content) != 0,
                "Content must not be empty"
            )
            dspy.Suggest(
                len(pred.filename) != 0,
                "Filename must not be empty"
            )
            dspy.Suggest(
                len(pred.filename) < 250,
                "Filename must be short and consice"
            )
            observation = self.write_file(pred.filename, pred.content)
            return dspy.Prediction(
                filename = pred.filename,
                content = pred.content,
                observation = observation,
            )
        else:
            raise NotImplementedError("Disabling inference for WriteFile not supported")

    def __deepcopy__(self, memo):
        cpy = (type)(self)(
            filesystem = self.filesystem,
            agent_state = self.agent_state,
        )
        cpy.predict = copy.deepcopy(self.predict)
        return cpy