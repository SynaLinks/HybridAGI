"""The duckduckgo tool. Copyright (C) 2024 SynaLinks. License: GPL-3.0"""

import dspy
from .base import BaseTool
from typing import Optional
from duckduckgo_search import DDGS
from ..output_parsers.query import QueryOutputParser
from ..output_parsers.prediction import PredictionOutputParser

class BrowseWebsiteSignature(dspy.Signature):
    """You will be given an objective, purpose and context
    Using the prompt to help you, you will infer the correct url"""
    objective = dspy.InputField(desc = "The long-term objective (what you are doing)")
    context = dspy.InputField(desc = "The previous actions (what you have done)")
    purpose = dspy.InputField(desc = "The purpose of the action (what you have to do now)")
    prompt = dspy.InputField(desc = "The action specific instructions (How to do it)")
    url = dspy.OutputField(desc = "The website to browse")

class BrowseWebsiteTool(BaseTool):

    def __init__(
            self,
            k: int = 2,
            lm: Optional[dspy.LM] = None,
        ):
        super().__init__(name = "BrowseWebsite", lm = lm)
        self.predict = dspy.Predict(BrowseWebsiteSignature)
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
            pred.url = self.prediction_parser.parse(pred.url, prefix="Url:", stop=["\n"])
            result = self.browser.browse_website(pred.url)
            return dspy.Prediction(
                url = pred.url,
                result = result,
            )
        else:
            result = self.browser.browse_website(prompt)
            return dspy.Prediction(
                url = prompt,
                result = result,
            )