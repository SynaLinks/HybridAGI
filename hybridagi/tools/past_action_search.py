"""The past action search. Copyright (C) 2024 SynaLinks. License: GPL-3.0"""

import copy
import dspy
from .base import BaseTool
from typing import Optional
from ..embeddings.base import BaseEmbeddings
from ..hybridstores.trace_memory.trace_memory import TraceMemory
from ..retrievers.action import ActionRetriever
from ..output_parsers.list_query import ListQueryOutputParser
from ..output_parsers.prediction import PredictionOutputParser

class ActionSearchSignature(dspy.Signature):
    """You will be given an objective, purpose and context
    Using the prompt to help you, you will infer the correct similarity search query"""
    objective = dspy.InputField(desc = "The long-term objective (what you are doing)")
    context = dspy.InputField(desc = "The previous actions (what you have done)")
    purpose = dspy.InputField(desc = "The purpose of the action (what you have to do now)")
    prompt = dspy.InputField(desc = "The action specific instructions (How to do it)")
    query = dspy.OutputField(desc = "The similarity search query")

class PastActionSearchTool(BaseTool):

    def __init__(
            self,
            trace_memory: TraceMemory,
            embeddings: BaseEmbeddings,
            distance_threshold: float = 1.3,
            k: int = 3,
            lm: Optional[dspy.LM] = None,
        ):
        super().__init__(name = "PastActionSearch", lm = lm)
        self.predict = dspy.Predict(ActionSearchSignature)
        self.trace_memory = trace_memory
        self.embeddings = embeddings
        self.distance_threshold = distance_threshold
        self.k = k
        self.retriever = ActionRetriever(
            trace_memory = trace_memory,
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
                query = query,
                past_actions = result.past_actions,
            )
        else:
            result = self.retriever(prompt)
            return dspy.Prediction(
                query = prompt,
                past_actions = result.past_actions,
            )

    def __deepcopy__(self, memo):
        cpy = (type)(self)(
            trace_memory = self.trace_memory,
            embeddings = self.embeddings,
            distance_threshold = self.distance_threshold,
            k = self.k,
        )
        cpy.predict = copy.deepcopy(self.predict)
        return cpy