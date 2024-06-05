"""The query facts tool. Copyright (C) 2024 SynaLinks. License: GPL-3.0"""

import copy
import dspy
from .base import BaseTool
from ..hybridstores.fact_memory.fact_memory import FactMemory
from ..output_parsers.cypher import CypherOutputParser
from ..output_parsers.prediction import PredictionOutputParser

class QueryFactsSignature(dspy.Signature):
    """You will be given an objective, purpose and context
    Using the prompt to help you, you will infer the correct Cypher query
    
    Use only the provided relationship types and properties.
    Do not use any other relationship types or properties that are not provided.
    If you cannot generate a Cypher statement based on the provided schema, explain the reason to the user.

    Note: Do not include any explanations or apologies in your responses."""
    objective = dspy.InputField(desc = "The long-term objective (what you are doing)")
    context = dspy.InputField(desc = "The previous actions (what you have done)")
    purpose = dspy.InputField(desc = "The purpose of the action (what you have to do now)")
    prompt = dspy.InputField(desc = "The action specific instructions (How to do it)")
    cypher_schema = dspy.InputField(desc= "The graph schema")
    cypher_query = dspy.OutputField(desc = "The correct Cypher query")

class QueryFactsTool(BaseTool):

    def __init__(
            self,
            fact_memory: FactMemory,
        ):
        super().__init__(name = "QueryFacts")
        self.predict = dspy.Predict(QueryFactsSignature)
        self.fact_memory = fact_memory
        self.cypher_parser = CypherOutputParser()
        self.prediction_parser = PredictionOutputParser()

    def query_facts(self, query: str) -> str:
        try:
            result = self.fact_memory.query(query)
            output = [r.values() for r in result.result_set]
            output.insert(0, list(result.keys()))
            return output
        except Exception as err:
            return str(err)
    
    def forward(
            self,
            context: str,
            objective: str,
            purpose: str,
            prompt: str,
            disable_inference: bool = False,
        ) -> dspy.Prediction:
        """Method to perform DSPy forward prediction"""
        if not disable_inference:
            pred = self.predict(
                objective = objective,
                context = context,
                purpose = purpose,
                prompt = prompt,
                cypher_schema = self.fact_memory.get_schema(refresh=True),
            )
            pred.cypher_query = self.prediction_parser.parse(pred.cypher_query, prefix="\n```cypher", stop=["\n```\n\n"])
            pred.cypher_query = self.cypher_parser.parse(pred.cypher_query)
            output = self.query_facts(pred.query)
            return dspy.Prediction(
                query = pred.query,
                output = output
            )
        else:
            output = self.query_facts(prompt)
            return dspy.Prediction(
                query = prompt,
                output = output
            )

    def __deepcopy__(self, memo):
        cpy = (type)(self)(
            fact_memory = self.fact_memory,
        )
        cpy.predict = copy.deepcopy(self.predict)
        return cpy