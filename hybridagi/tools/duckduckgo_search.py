import dspy
from .base import BaseTool
from typing import Optional
from duckduckgo_search import DDGS

class DuckDuckGoSearchSignature(dspy.Signature):
    """Infer a duckduckgo search query to answer question"""
    objective = dspy.InputField(desc = "What you are doing")
    context = dspy.InputField(desc = "What you have done")
    purpose = dspy.InputField(desc = "What you have to do now")
    prompt = dspy.InputField(desc = "How to do it")
    query = dspy.OutputField(desc = "The duckduckgo search query")

class DuckDuckGoSearchTool(BaseTool):

    def __init__(self, k: int = 3):
        super().__init__(name = "DuckDuckGoSearch")
        self.predict = dspy.Predict(DuckDuckGoSearchSignature)
        self.k = k
    
    def forward(
            self,
            context: str,
            objective: str,
            purpose: str,
            prompt: str,
            disable_inference: bool = False,
            k: Optional[int] = None,
        ) -> dspy.Prediction:
        if not disable_inference:
            pred = self.predict(
                objective = objective,
                context = context,
                purpose = purpose,
                prompt = prompt,
            )
            query = pred.query
            result = DDGS().text(query, max_results=k if k else self.k)
            return dspy.Prediction(
                query = query,
                results = result,
            )
        else:
            result = DDGS().text(prompt, max_results=k if k else self.k)
            return dspy.Prediction(
                query = prompt,
                results = result,
            )