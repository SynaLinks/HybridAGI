"""The duckduckgo tool. Copyright (C) 2024 SynaLinks. License: GPL-3.0"""

import dspy
import copy
from .base import BaseTool
from typing import Optional
from duckduckgo_search import DDGS
from ..output_parsers.query import QueryOutputParser
from ..output_parsers.prediction import PredictionOutputParser

class DuckDuckGoSearchSignature(dspy.Signature):
    """You will be given an objective, purpose and context
    Using the prompt to help you, you will infer the correct DuckDuckGo query"""
    objective = dspy.InputField(desc = "The long-term objective (what you are doing)")
    context = dspy.InputField(desc = "The previous actions (what you have done)")
    purpose = dspy.InputField(desc = "The purpose of the action (what you have to do now)")
    prompt = dspy.InputField(desc = "The action specific instructions (How to do it)")
    query = dspy.OutputField(desc = "The DuckDuckGo search query (only few words)")

class DuckDuckGoSearchTool(BaseTool):

    def __init__(
            self,
            k: int = 5,
            lm: Optional[dspy.LM] = None,
        ):
        super().__init__(name = "DuckDuckGoSearch", lm = lm)
        self.predict = dspy.Predict(DuckDuckGoSearchSignature)
        self.k = k
        self.query_parser = QueryOutputParser()
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
            pred.query = self.query_parser.parse(pred.query)
            result = DDGS().text(pred.query, max_results=k if k else self.k)
            return dspy.Prediction(
                search_query = pred.query,
                results = result,
            )
        else:
            result = DDGS().text(prompt, max_results=k if k else self.k)
            return dspy.Prediction(
                search_query = prompt,
                results = result,
            )

    def __deepcopy__(self, memo):
        cpy = (type)(self)(
            k = self.k,
            lm = self.lm,
        )
        cpy.predict = copy.deepcopy(self.predict)
        return cpy