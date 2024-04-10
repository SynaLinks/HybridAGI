"""The program search tool. Copyright (C) 2024 SynaLinks. License: GPL-3.0"""

import copy
import dspy
from .base import BaseTool
from typing import Optional
from ..embeddings.base import BaseEmbeddings
from ..hybridstores.program_memory.program_memory import ProgramMemory
from ..retrievers.program import ProgramRetriever

class ProgramSearchSignature(dspy.Signature):
    """Infer one search query to retrieve routine programs"""
    objective = dspy.InputField(desc = "The long-term objective (what you are doing)")
    context = dspy.InputField(desc = "The previous actions (what you have done)")
    purpose = dspy.InputField(desc = "The purpose of the action (what you have to do now)")
    prompt = dspy.InputField(desc = "The action specific instructions (How to do it)")
    query = dspy.OutputField(desc = "The similarity based search query (only ONE sentence)")

class ProgramSearchTool(BaseTool):

    def __init__(
            self,
            program_memory: ProgramMemory,
            embeddings: BaseEmbeddings,
            distance_threshold: float = 1.25,
            k: int = 3,
        ):
        super().__init__(name = "ProgramSearch")
        self.predict = dspy.Predict(ProgramSearchSignature)
        self.program_memory = program_memory
        self.embeddings = embeddings
        self.distance_threshold = distance_threshold
        self.k = k
        self.retriever = ProgramRetriever(
            program_memory = program_memory,
            embeddings = embeddings,
            distance_threshold = self.distance_threshold,
            k = self.k,
        )
    
    def forward(
            self,
            context: str,
            objective: str,
            purpose: str,
            prompt: str,
            disable_inference: bool = False,
            k: Optional[int] = None,
        ) -> dspy.Prediction:
        """Method to perform DSPy forward prediction"""
        if not disable_inference:
            prediction = self.predict(
                objective = objective,
                context = context,
                purpose = purpose,
                prompt = prompt,
            )
            query = prediction.query
            result = self.retriever(query)
            return dspy.Prediction(
                query = query,
                programs = result.programs,
            )
        else:
            result = self.retriever(prompt)
            return dspy.Prediction(
                query = prompt,
                programs = result.programs,
            )

    def __deepcopy__(self, memo):
        cpy = (type)(self)(
            program_memory = self.program_memory,
            embeddings = self.embeddings,
            distance_threshold = self.distance_threshold,
            k = self.k,
        )
        cpy.predict = copy.deepcopy(self.predict)
        return cpy