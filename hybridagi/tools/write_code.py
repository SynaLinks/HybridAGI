"""The write code tool. Copyright (C) 2024 SynaLinks. License: GPL-3.0"""

import asyncio
import copy
import dspy
from .base import BaseTool
from typing import Optional
from ..hybridstores.filesystem.filesystem import FileSystem
from ..output_parsers.path import PathOutputParser
from ..output_parsers.prediction import PredictionOutputParser
from ..types.state import AgentState
from codeshield.cs import CodeShield

class WriteCodeSignature(dspy.Signature):
    """You will be given an objective, purpose and context
    Using the prompt to help you, you will infer the correct filename and code
    
    Note: Never give an apology or explain what you are doing."""
    objective = dspy.InputField(desc = "The long-term objective (what you are doing)")
    context = dspy.InputField(desc = "The previous actions (what you have done)")
    purpose = dspy.InputField(desc = "The purpose of the action (what you have to do now)")
    prompt = dspy.InputField(desc = "The action specific instructions (How to do it)")
    filename = dspy.OutputField(desc = "The name of the file (short and concise)")
    code = dspy.OutputField(desc = "The code to write")

class WriteCodeTool(BaseTool):

    def __init__(
            self,
            filesystem: FileSystem,
            agent_state: AgentState,
            lm: Optional[dspy.LM] = None,
        ):
        super().__init__(name = "WriteCode", lm = lm)
        self.predict = dspy.Predict(WriteCodeSignature)
        self.agent_state = agent_state
        self.filesystem = filesystem
        self.path_parser = PathOutputParser()
        self.prediction_parser = PredictionOutputParser()

    def write_code(self, filename: str, content: str) -> str:
        observation = ""
        code_shield_observation = ""
        result = asyncio.run(CodeShield.scan_code(content))
        if result.is_insecure:
            if result.recommended_treatment == "block":
                code_shield_observation = "Error: Code Security issues found, blocking the code"
                return code_shield_observation
            if result.recommended_treatment == "warn":
                code_shield_observation = "Warning: The generated snippet contains insecure code"
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
            observation = "Successfully written"
        except Exception as err:
            return str(err) + code_shield_observation
        return observation + code_shield_observation
    
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
            pred.filename = self.prediction_parser.parse(pred.filename, prefix="Filename:", stop=["\n"])
            pred.filename = self.path_parser.parse(pred.filename)
            pred.code = self.prediction_parser.parse(pred.code, prefix="Code:")
            pred.code = self.prediction_parser.parse(pred.code, prefix="```", stop=["\n```\n\n"])
            dspy.Suggest(
                len(pred.code) != 0,
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
            observation = self.write_code(pred.filename, pred.code)
            return dspy.Prediction(
                filename = pred.filename,
                code = pred.code,
                observation = observation,
            )
        else:
            raise NotImplementedError("Disabling inference for WriteFile not supported")

    def __deepcopy__(self, memo):
        cpy = (type)(self)(
            filesystem = self.filesystem,
            agent_state = self.agent_state,
            lm = self.lm,
        )
        cpy.predict = copy.deepcopy(self.predict)
        return cpy