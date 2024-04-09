"""The program search tool. Copyright (C) 2024 SynaLinks. License: GPL-3.0"""

import dspy
import copy
from .base import BaseTool
from typing import Optional
from ..embeddings.base import BaseEmbeddings
from ..hybridstores.filesystem.filesystem import FileSystem
from ..retrievers.document import DocumentRetriever

class DocumentSearchSignature(dspy.Signature):
    """Infer one search query to retrieve documents passages"""
    objective = dspy.InputField(desc = "The long-term objective (what you are doing)")
    context = dspy.InputField(desc = "The previous actions (what you have done)")
    purpose = dspy.InputField(desc = "The purpose of the action (what you have to do now)")
    prompt = dspy.InputField(desc = "The action specific instructions (How to do it)")
    query = dspy.OutputField(desc = "The similarity based search query (only ONE sentence)")

class DocumentSearchTool(BaseTool):

    def __init__(
            self,
            filesystem: FileSystem,
            embeddings: BaseEmbeddings,
            distance_threshold: float = 1.2,
            k: int = 3,
        ):
        super().__init__(name = "DocumentSearch")
        self.predict = dspy.Predict(DocumentSearchSignature)
        self.filesystem = filesystem
        self.embeddings = embeddings
        self.distance_threshold = distance_threshold
        self.k = k
        self.retriever = DocumentRetriever(
            filesystem = filesystem,
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
                passages = result.passages,
            )
        else:
            result = self.retriever(prompt)
            return dspy.Prediction(
                query = prompt,
                passages = result.passages,
            )

    def __deepcopy__(self, memo):
        cpy = (type)(self)(
            filesystem = self.filesystem,
            embeddings = self.embeddings,
            distance_threshold = self.distance_threshold,
            k = self.k,
        )
        cpy.predict = copy.deepcopy(self.predict)
        return cpy