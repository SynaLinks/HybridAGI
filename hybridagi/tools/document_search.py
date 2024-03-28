import dspy
from .base import BaseTool
from typing import Optional
from ..embeddings.base import BaseEmbeddings
from ..retrievers.document import DocumentRetriever

class DocumentSearchSignature(dspy.Signature):
    """Infer a search query to retrieve documents to answer question"""
    trace = dspy.InputField(desc = "Previous actions")
    objective = dspy.InputField(desc = "Long-term objective")
    purpose = dspy.InputField(desc = "Short-term purpose")
    prompt = dspy.InputField(desc = "Task specific instructions")
    query = dspy.OutputField(desc = "The similarity based search query")

class DocumentSearchTool(BaseTool):

    def __init__(
            self,
            index_name: str,
            embeddings: BaseEmbeddings,
            graph_index: str = "filesystem",
            hostname: str = "localhost",
            port: int = 6379,
            username: str = "",
            password: str = "",
            k: int = 3,
        ):
        super().__init__(name = "DocumentSearch")
        self.predict = dspy.Predict(DocumentSearchSignature)
        self.retriever = DocumentRetriever(
            index_name = index_name,
            embeddings = embeddings,
            graph_index = graph_index,
            hostname = hostname,
            port = port,
            username = username,
            password = password,
            k = self.k,
        )
    
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