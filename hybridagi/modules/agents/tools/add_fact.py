import dspy
import copy
from .tool import Tool
from typing import Optional, Callable
from hybridagi.core.datatypes import (
    Document,
    FactList,
    ToolInput,
)
from hybridagi.memory import FactMemory
from hybridagi.core.pipeline import Pipeline
from hybridagi.output_parsers import PredictionOutputParser

class AddFactSignature(dspy.Signature):
    objective = dspy.InputField(desc = "The long-term objective (what you are doing)")
    context = dspy.InputField(desc = "The previous actions (what you have done)")
    purpose = dspy.InputField(desc = "The purpose of the action (what you have to do now)")
    prompt = dspy.InputField(desc = "The action specific instructions (How to do it)")
    document = dspy.OutputField(desc = "The factual knowledge to save")

class AddFactTool(Tool):
    
    def __init__(
            self,
            fact_memory: FactMemory,
            pipeline: Pipeline,
            name = "AddFact",
            lm: Optional[dspy.LM] = None
        ):
        super().__init__(name=name, lm=lm)
        self.fact_memory = fact_memory
        self.pipeline = pipeline
        self.predict = dspy.Predict(AddFactSignature)
        self.prediction_parser = PredictionOutputParser()
        
    def forward(self, tool_input: ToolInput) -> FactList:
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
            facts = self.pipeline(document)
            self.fact_memory.update(facts)
            return facts
        else:
            document = Document(text=tool_input.prompt)
            facts = self.pipeline(document)
            self.fact_memory.update(facts)
            return facts
        
    def __deepcopy__(self, memo):
        cpy = (type)(self)(
            fact_memory = self.fact_memory,
            name = self.name,
            pipeline = self.pipeline,
            lm = self.lm,
        )
        cpy.predict = copy.deepcopy(self.predict)
        return cpy