import dspy
import copy
from .tool import Tool
from typing import Optional, Callable
from hybridagi.core.datatypes import (
    Document,
    DocumentList,
    ToolInput,
)
from hybridagi.memory import DocumentMemory
from hybridagi.core.pipeline import Pipeline
from hybridagi.output_parsers import PredictionOutputParser

class AddDocumentSignature(dspy.Signature):
    objective = dspy.InputField(desc = "The long-term objective (what you are doing)")
    context = dspy.InputField(desc = "The previous actions (what you have done)")
    purpose = dspy.InputField(desc = "The purpose of the action (what you have to do now)")
    prompt = dspy.InputField(desc = "The action specific instructions (How to do it)")
    document = dspy.OutputField(desc = "The text knowledge to save")

class AddDocumentTool(Tool):
    
    def __init__(
            self,
            document_memory: DocumentMemory,
            pipeline: Pipeline,
            name = "AddDocument",
            lm: Optional[dspy.LM] = None
        ):
        super().__init__(name=name, lm=lm)
        self.document_memory = document_memory
        self.pipeline = pipeline
        self.predict = dspy.Predict(AddDocumentSignature)
        self.prediction_parser = PredictionOutputParser()
        
    def forward(self, tool_input: ToolInput) -> DocumentList:
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
            pred.document = self.prediction_parser.parse(
                pred.document,
                prefix = "Document:",
            )
            pred.document = pred.document.strip("\"")
            document = Document(text=pred.document)
            docs = self.pipeline(document)
            self.document_memory.update(docs)
            return docs
        else:
            document = Document(text=tool_input.prompt)
            docs = self.pipeline(document)
            self.document_memory.update(docs)
            return docs
        
    def __deepcopy__(self, memo):
        cpy = (type)(self)(
            document_memory = self.document_memory,
            name = self.name,
            pipeline = self.pipeline,
            lm = self.lm,
        )
        cpy.predict = copy.deepcopy(self.predict)
        return cpy