import dspy
from .tool import Tool
from typing import Optional, Callable
from hybridagi.core.datatypes import (
    ToolInput,
    Query,
    QueryWithFacts,
)
from hybridagi.output_parsers import PredictionOutputParser
from hybridagi.output_parsers import QueryListOutputParser

class QueryFactSignature(dspy.Signature):
    objective = dspy.InputField(desc = "The long-term objective (what you are doing)")
    context = dspy.InputField(desc = "The previous actions (what you have done)")
    purpose = dspy.InputField(desc = "The purpose of the action (what you have to do now)")
    prompt = dspy.InputField(desc = "The action specific instructions (How to do it)")
    query = dspy.OutputField(desc = "The cypher query without additional details")
    
class QueryWithResult():
    query: str
    result: List[List[str]]
    
    def to_dict(self):
        return {"query": self.query, "result": self.result}

class QueryFactTool(Tool):
    def __init__(
            self,
            query_fact: dspy.Module,
            name: str = "QueryFact",
            lm: Optional[dspy.LM] = None,
        ):
        super().__init__(name = name, lm = lm)
        self.query_fact = query_fact
        self.predict = dspy.Predict(FactSearchSignature)
        self.prediction_parser = PredictionOutputParser()
        self.query_parser = QueryListOutputParser()
    
    def forward(self, tool_input: ToolInput) -> QueryWithResult:
        if not isinstance(tool_input, ToolInput):
            raise ValueError(f"{type(self).__name__} input must be a ToolInput")
        if not tool_input.disable_inference:
            with dspy.context(lm=self.lm if self.lm is not None else dspy.settings.lm):
                pred = self.predict(
                    objective = tool_input.objective,
                    context = tool_input.context,
                    purpose = tool_input.purpose,
                    prompt = tool_input.prompt,
                )
            pred.query = self.prediction_parser.parse(
                pred.query,
                prefix = "Query:",
            )
            query = self.query_parser.parse(pred.query)
            query_with_results = self.query_fact(query)
            return query_with_results
        else:
            query = self.query_parser.parse(tool_input.prompt)
            query_with_results = self.query_fact(query)
            return query_with_results
        
    def __deepcopy__(self, memo):
        cpy = (type)(self)(
            query_fact = self.query_fact,
            name = self.name,
            lm = self.lm,
        )
        cpy.predict = copy.deepcopy(self.predict)
        cpy.query_fact = copy.deepcopy(self.query_fact)
        return cpy