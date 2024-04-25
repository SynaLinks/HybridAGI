"""The duckduckgo tool. Copyright (C) 2024 SynaLinks. License: GPL-3.0"""

import dspy
from .base import BaseTool
from typing import Optional
from duckduckgo_search import DDGS
from ..parsers.query import QueryOutputParser
from ..parsers.prediction import PredictionOutputParser

class DuckDuckGoSearchSignature(dspy.Signature):
    """You will be given an objective, purpose and context
    Using the prompt to help you, you will infer the correct Google query"""
    objective = dspy.InputField(desc = "The long-term objective (what you are doing)")
    context = dspy.InputField(desc = "The previous actions (what you have done)")
    purpose = dspy.InputField(desc = "The purpose of the action (what you have to do now)")
    prompt = dspy.InputField(desc = "The action specific instructions (How to do it)")
    query = dspy.OutputField(desc = "The Google search query (only few words)")

class DuckDuckGoSearchTool(BaseTool):

    def __init__(self, k: int = 3):
        super().__init__(name = "DuckDuckGoSearch")
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
            prediction = self.predict(
                objective = objective,
                context = context,
                purpose = purpose,
                prompt = prompt,
            )
            query = self.prediction_parser.parse(prediction.query, prefix="Query:", stop=["\n"])
            query = self.query_parser.parse(query)
            result = DDGS().text(query, max_results=k if k else self.k)
            return dspy.Prediction(
                search_query = query,
                results = result,
            )
        else:
            result = DDGS().text(prompt, max_results=k if k else self.k)
            return dspy.Prediction(
                search_query = prompt,
                results = result,
            )