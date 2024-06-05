"""The entity search tool. Copyright (C) 2024 SynaLinks. License: GPL-3.0"""

import copy
import dspy
from .base import BaseTool
from typing import Optional
from ..embeddings.base import BaseEmbeddings
from ..hybridstores.fact_memory.fact_memory import FactMemory
from ..retrievers.entity import EntityRetriever
from ..output_parsers.list_query import ListQueryOutputParser
from ..output_parsers.prediction import PredictionOutputParser

class EntitySearchSignature(dspy.Signature):
    """You will be given an objective, purpose and context
    Using the prompt to help you, you will infer the correct name to search"""
    objective = dspy.InputField(desc = "The long-term objective (what you are doing)")
    context = dspy.InputField(desc = "The previous actions (what you have done)")
    purpose = dspy.InputField(desc = "The purpose of the action (what you have to do now)")
    prompt = dspy.InputField(desc = "The action specific instructions (How to do it)")
    name = dspy.OutputField(desc = "The name of the entity to search")

class EntitySearchTool(BaseTool):

    def __init__(
            self,
            fact_memory: FactMemory,
            embeddings: BaseEmbeddings,
            distance_threshold: float = 1.25,
            k: int = 3,
        ):
        super().__init__(name = "EntitySearch")
        self.predict = dspy.Predict(EntitySearchSignature)
        self.fact_memory = fact_memory
        self.embeddings = embeddings
        self.distance_threshold = distance_threshold
        self.k = k
        self.retriever = EntityRetriever(
            fact_memory = fact_memory,
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
            pred = self.predict(
                objective = objective,
                context = context,
                purpose = purpose,
                prompt = prompt,
            )
            pred.name = self.prediction_parser.parse(pred.name, prefix="Name:", stop=["\n"])
            query = self.query_parser.parse(pred.name)
            result = self.retriever(query)
            return dspy.Prediction(
                search_query = query,
                entities = result.entities,
            )
        else:
            result = self.retriever(prompt)
            return dspy.Prediction(
                search_query = prompt,
                entities = result.entities,
            )

    def __deepcopy__(self, memo):
        cpy = (type)(self)(
            fact_memory = self.fact_memory,
            embeddings = self.embeddings,
            distance_threshold = self.distance_threshold,
            k = self.k,
        )
        cpy.predict = copy.deepcopy(self.predict)
        return cpy