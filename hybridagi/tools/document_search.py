"""The program search tool. Copyright (C) 2024 SynaLinks. License: GPL-3.0"""

import copy
import dspy
from .base import BaseTool
from typing import Optional
from ..embeddings.base import BaseEmbeddings
from ..hybridstores.filesystem.filesystem import FileSystem
from ..retrievers.document import DocumentRetriever
from ..output_parsers.list_query import ListQueryOutputParser
from ..output_parsers.prediction import PredictionOutputParser

class DocumentSearchSignature(dspy.Signature):
    """You will be given an objective, purpose and context
    Using the prompt to help you, you will infer the correct similarity search query"""
    objective = dspy.InputField(desc = "The long-term objective (what you are doing)")
    context = dspy.InputField(desc = "The previous actions (what you have done)")
    purpose = dspy.InputField(desc = "The purpose of the action (what you have to do now)")
    prompt = dspy.InputField(desc = "The action specific instructions (How to do it)")
    query = dspy.OutputField(desc = "The search query (only few words)")

class DocumentSearchTool(BaseTool):

    def __init__(
            self,
            filesystem: FileSystem,
            embeddings: BaseEmbeddings,
            distance_threshold: float = 1.25,
            k: int = 3,
            lm: Optional[dspy.LM] = None,
        ):
        super().__init__(name = "DocumentSearch", lm = lm)
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
        self.query_parser = ListQueryOutputParser()
        self.prediction_parser = PredictionOutputParser()
    
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
            with dspy.context(lm=self.lm if self.lm is not None else dspy.settings.lm):
                pred = self.predict(
                    objective = objective,
                    context = context,
                    purpose = purpose,
                    prompt = prompt,
                )
            pred.query = self.prediction_parser.parse(pred.query, prefix="Query:", stop=["\n"])
            query = self.query_parser.parse(pred.query)
            result = self.retriever(query)
            return dspy.Prediction(
                search_query = query,
                passages = result.passages,
            )
        else:
            result = self.retriever(prompt)
            return dspy.Prediction(
                search_query = prompt,
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