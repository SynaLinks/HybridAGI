import dspy
from .base import BaseTool
from typing import Optional
from duckduckgo_search import DDGS

class DuckDuckGoSearchSignature(dspy.Signature):
    """Infer a duckduckgo search query to answer question"""
    trace = dspy.InputField(desc = "Previous actions")
    objective = dspy.InputField(desc = "Long-term objective")
    purpose = dspy.InputField(desc = "Short-term purpose")
    prompt = dspy.InputField(desc = "Task specific instructions")
    query = dspy.OutputField(desc = "The duckduckgo search query")

class DuckDuckGoSearchTool(BaseTool):

    def __init__(self, k: int = 3):
        super().__init__(name = "DuckDuckGoSearch")
        self.predict = dspy.Predict(DuckDuckGoSearchSignature)
        self.k = k
    
    def forward(
            self,
            trace: str,
            objective: str,
            purpose: str,
            prompt: str,
            disable_inference: bool = False,
            stop: Optional[str] = None,
            k: Optional[int] = None,
        ) -> dspy.Prediction:
        if not disable_inference:
            pred = self.predict(
                objective = objective,
                purpose = purpose,
                trace = trace,
                prompt = prompt,
                stop = stop,
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