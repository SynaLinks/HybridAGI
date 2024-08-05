import dspy
import copy
from .tool import Tool
from typing import Optional, Callable
from hybridagi.core.datatypes import (
    ToolInput,
    Query,
    AgentStepList,
)
from hybridagi.output_parsers import PredictionOutputParser
from hybridagi.output_parsers import QueryOutputParser

class PastActionSearchSignature(dspy.Signature):
    objective = dspy.InputField(desc = "The long-term objective (what you are doing)")
    context = dspy.InputField(desc = "The previous actions (what you have done)")
    purpose = dspy.InputField(desc = "The purpose of the action (what you have to do now)")
    prompt = dspy.InputField(desc = "The action specific instructions (How to do it)")
    query = dspy.OutputField(desc = "The similarity search query")

class PastActionSearchTool(Tool):
    def __init__(
            self,
            retriever: dspy.Module,
            name: str = "PastActionSearch",
            lm: Optional[dspy.LM] = None,
        ):
        super().__init__(name = name, lm = lm)
        self.retriever = retriever
        self.predict = dspy.Predict(PastActionSearchSignature)
        self.prediction_parser = PredictionOutputParser()
        self.query_parser = QueryOutputParser()
        
    def action_search(self, query: str):
        retriver_input = Query(query=query)
        return self.retriever(retriver_input)
    
    def forward(self, tool_input: ToolInput) -> AgentStepList:
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
            pred.query = self.query_parser.parse(pred.query)
            action_list = self.action_search(pred.query)
            return action_list
        else:
            action_list = self.action_search(tool_input.prompt)
            return action_list
        
    def __deepcopy__(self, memo):
        cpy = (type)(self)(
            retriever = self.retriever,
            name = self.name,
            lm = self.lm,
        )
        cpy.predict = copy.deepcopy(self.predict)
        cpy.retriever = copy.deepcopy(self.retriever)
        return cpy