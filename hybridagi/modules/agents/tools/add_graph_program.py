import dspy
import copy
from .tool import Tool
from typing import Optional, Callable
from hybridagi.core.datatypes import (
    Document,
    DocumentList,
    ToolInput,
)
from hybridagi.memory import ProgramMemory
from hybridagi.core.pipeline import Pipeline
from hybridagi.output_parsers import PredictionOutputParser
from hybridagi.output_parsers import CypherOutputParser

class AddProgramSignature(dspy.Signature):
    """
    Infer the name field using snake case it should reflect the purpose of the graph, be concise.
    
    To infer the cypher field, you should always write the Cypher CREATE query inside markdown quotes like this:
    
    ```cypher
    // @desc: The description of the workflow
    CREATE
    ... (the graph data)
    ```
    
    You can comment what you do, as long as the final Cypher CREATE query is under the right quotes.
    """
    objective = dspy.InputField(desc = "The long-term objective (what you are doing)")
    context = dspy.InputField(desc = "The previous actions (what you have done)")
    purpose = dspy.InputField(desc = "The purpose of the action (what you have to do now)")
    prompt = dspy.InputField(desc = "The action specific instructions (How to do it)")
    name = dspy.OutputField(desc = "The name of the cypher file")
    cypher = dspy.OutputField(desc = "The cyher graph to save")

class AddGraphProgramTool(Tool):
    
    def __init__(
            self,
            program_memory: ProgramMemory,
            pipeline: Pipeline,
            name = "AddGraphProgram",
            lm: Optional[dspy.LM] = None
        ):
        super().__init__(name=name, lm=lm)
        self.program_memory = program_memory
        self.pipeline = pipeline
        self.predict = dspy.Predict(AddDocumentSignature)
        self.prediction_parser = PredictionOutputParser()
        self.cypher_parser = CypherOutputParser()        
        
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
                pred.name = self.prediction_parser(prefix="Name:", stop=[" ", "."])
                pred.cypher = self.prediction_parser(pred.cypher, prefix="Cypher:")
                pred.cypher = self.cypher_parser.parse(pred.cypher)
                graph_program = GraphProgram(name=name).from_cypher(program)
                self.program_memory.update(graph_program)
            return graph_program
        else:
            raise NotImplementedError(f"{type(self).__name__} does not support disabling inference")