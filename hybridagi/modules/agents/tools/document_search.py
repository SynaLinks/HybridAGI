import dspy
import copy
from .tool import Tool
from typing import Optional, Callable
from hybridagi.core.datatypes import (
    ToolInput,
    Query,
    QueryWithDocuments,
)
from hybridagi.output_parsers import PredictionOutputParser
from hybridagi.output_parsers import QueryListOutputParser

class DocumentSearchSignature(dspy.Signature):
    objective = dspy.InputField(desc = "The long-term objective (what you are doing)")
    context = dspy.InputField(desc = "The previous actions (what you have done)")
    purpose = dspy.InputField(desc = "The purpose of the action (what you have to do now)")
    prompt = dspy.InputField(desc = "The action specific instructions (How to do it)")
    query = dspy.OutputField(desc = "The comma separated similarity search queries")

class DocumentSearchTool(Tool):
    def __init__(
            self,
            retriever: dspy.Module,
            name: str = "DocumentSearch",
            description = "Usefull to search for documents in memory",
            lm: Optional[dspy.LM] = None,
        ):
        super().__init__(
            name = name,
            description = description,
            lm = lm,
        )
        self.retriever = retriever
        self.predict = dspy.Predict(DocumentSearchSignature)
        self.prediction_parser = PredictionOutputParser()
        self.query_parser = QueryListOutputParser()
    
    def forward(self, tool_input: ToolInput) -> QueryWithDocuments:
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
            query_with_documents = self.retriever(query)
            return query_with_documents
        else:
            query_with_documents = self.document_search(tool_input.prompt)
            return query_with_documents
        
    def __deepcopy__(self, memo):
        cpy = (type)(self)(
            retriever = self.retriever,
            name = self.name,
            lm = self.lm,
        )
        cpy.predict = copy.deepcopy(self.predict)
        cpy.retriever = copy.deepcopy(self.retriever)
        return cpy