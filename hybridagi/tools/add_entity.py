"""The query facts tool. Copyright (C) 2024 SynaLinks. License: GPL-3.0"""

import copy
import dspy
from .base import BaseTool
from ..hybridstores.fact_memory.fact_memory import FactMemory
from ..parsers.cypher import CypherOutputParser
from ..parsers.prediction import PredictionOutputParser

class AddEntitySignature(dspy.Signature):
    """You will be given an objective, purpose and context
    Using the prompt to help you, you will infer the correct entity name, label and description"""
    objective = dspy.InputField(desc = "The long-term objective (what you are doing)")
    context = dspy.InputField(desc = "The previous actions (what you have done)")
    purpose = dspy.InputField(desc = "The purpose of the action (what you have to do now)")
    prompt = dspy.InputField(desc = "The action specific instructions (How to do it)")
    schema = dspy.InputField(desc= "The graph schema")
    name = dspy.OutputField(desc= "The entity name")
    label = dspy.OutputField(desc= "The entity label")
    description = dspy.OutputField(desc = "The entity description")

class AddEntityTool(BaseTool):

    def __init__(
            self,
            fact_memory: FactMemory,
        ):
        super().__init__(name = "AddEntity")
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
            dspy.Suggest(True, f"This query returns an error: {str(err)}"+
            "Give me a improved query that works without any explanations or apologies")
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
                schema = self.fact_memory.get_schema(refresh=True),
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