import dspy
from .base import BaseTool
from typing import Optional
from duckduckgo_search import DDGS

class DuckDuckGoSearchSignature(dspy.Signature):
    """Infer a DuckDuckGo search query to answer question"""
    objective = dspy.InputField(desc = "The long-term objective (what you are doing)")
    context = dspy.InputField(desc = "The previous actions (what you have done)")
    purpose = dspy.InputField(desc = "The purpose of the action (what you have to do now)")
    prompt = dspy.InputField(desc = "The action specific instructions (How to do it)")
    query = dspy.OutputField(desc = "The DuckDuckGo search query (ONE question only)")

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
            query = pred.query.strip("\"").strip()
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