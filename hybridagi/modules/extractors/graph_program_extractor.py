import dspy
from hybridagi.core.datatypes import Document, DocumentList, GraphProgramList
from hybridagi.core.graph_program import GraphProgram
from typing import List, Optional, Union
from enum import Enum
from pydantic import BaseModel, Field
from tqdm import tqdm
from hybridagi.output_parsers import CypherOutputParser
from hybridagi.modules.agents.tools import Tool
    
class GraphProgramExtractorSignature(dspy.Signature):
    """You will be given a `document` `tools` and `programs`, your task is to infer the `graph` field
To infer the `graph` field, ensure to follow the following Cypher schema:

Nodes:
- Action: Action nodes represent specific actions. These nodes are responsible for the use of a tool within the program. Each action node contains the name of the tool used, the purpose of the action and a description of how to infer the tool's input parameters.
- Decision: Decision nodes are used to make choices within the routine. These nodes have outgoing edges that branch off to different paths or actions based on certain conditions or criteria. The labels on the outgoing edges of decision nodes specify the possible answers. These labels guide the flow of the program to different branches, creating a decision graph.
- Program: Program nodes allow the system to call existing routines.
- Control: Control nodes help define the program's overall structure and execution flow. The Start Node marks the beginning of the program's execution. It doesn't perform an action but acts as an entry point. The End Node marks the conclusion or termination of the program. It doesn't perform an action but acts as an exit point.

Properties:
- Action:
    - id: The unique identifier of the step
    - purpose: The purpose of the step
    - prompt: The prompt to help in using the tool
    - tool: the name of the tool to use
- Decision:
    - id: The unique if of the step
    - purpose: The purpose of the step
    - question: The question to ask
- Program:
    - id: The unique id of the step
    - purpose: The purpose of the call
    - program: The sub-routine to call
- Control:
    - id: The unique id (start or end)
    
Relationships:
- NEXT: This edge represent the sequentiality of the steps
- Decision output edges: The output edges of decision nodes give the possible answers to the system like YES, NO, MAYBE or any relevant answer

Ensure that you follow the following format:

```cypher
CREATE
// Nodes declaration
(start:Control {id: "start"}),
(end:Control {id: "end"}),
...
(ask_user:Action {
  id: "action",
  purpose: "The purpose of the Action",
  prompt: "The prompt to use to help in using the tool",
  tool: "ToolName",
}),
// ...
(is_answer_correct:Decision {
  id: "action",
  purpose: "The purpose of the decision",
  question: "The question to ask",
}),
... (N times)
// Structure declaration
(start)-[:NEXT]->(action),
// ...
(is_answer_correct)-[YES]->(next_step),
(is_answer_correct)-[NO]->(next_step),
(is_answer_correct)-[MAYBE]->(next_step), // You can use any number of output edges for decision nodes 
... (N times)
(action_n)-[:NEXT]->(end)
```

Modify the example to accuratly reflect the given plan
Choose ids that reflect the purpose of each step, like 'answer', 'write_draft' etc.
Make sure to use the correct tool specificed in the given plan.
Make sure to connect the last step to the end node.
Make sure to correctly infer the structure, using the steps ids.
For EVERY nodes, make sure to populate the `purpose` field with a concise purpose that should reflect the goal of the step (just few words).
Make sure that the start and end nodes are correctly connected
"""
    document: str = dspy.InputField(desc="The input document")
    tools: str = dspy.InputField(desc="The available tools that you can use")
    routines: str = dspy.InputField(desc="The sub-routines that you can use")
    graph: str = dspy.OutputField(desc="The output graph")
    
class CorrectGraphProgram(dspy.Signature):
    """You will be given a `input_graph`, `tools`, `routines` and `errors`, your task is to infer the `graph` field.
Your task is to address the given errors and output a corrected version of the graph, preserve the same format.
No NOT change the correct parts of the graph nor the format and ONLY modify what is pointed by the errors

Ensure to follow the following Cypher schema:

Nodes:
- Action: Action nodes represent specific actions. These nodes are responsible for the use of a tool within the program. Each action node contains the name of the tool used, the purpose of the action and a description of how to infer the tool's input parameters.
- Decision: Decision nodes are used to make choices within the routine. These nodes have outgoing edges that branch off to different paths or actions based on certain conditions or criteria. The labels on the outgoing edges of decision nodes specify the possible answers. These labels guide the flow of the program to different branches, creating a decision graph.
- Program: Program nodes allow the system to call existing routines.
- Control: Control nodes help define the program's overall structure and execution flow. The Start Node marks the beginning of the program's execution. It doesn't perform an action but acts as an entry point. The End Node marks the conclusion or termination of the program. It doesn't perform an action but acts as an exit point.

Properties:
- Action:
    - id: The unique identifier of the step
    - purpose: The purpose of the step
    - prompt: The prompt to help in using the tool
    - tool: the name of the tool to use
- Decision:
    - id: The unique if of the step
    - purpose: The purpose of the step
    - question: The question to ask
- Program:
    - id: The unique id of the step
    - purpose: The purpose of the call
    - program: The sub-routine to call
- Control:
    - id: The unique id (start or end)
    
Relationships:
- NEXT: This edge represent the sequentiality of the steps
- Decision output edges: The output edges of decision nodes give the possible answers to the system like YES, NO, MAYBE or any relevant answer

Ensure that you follow the following format:

```cypher
CREATE
// Nodes declaration
(start:Control {id: "start"}),
(end:Control {id: "end"}),
...
(ask_user:Action {
  id: "action",
  purpose: "The purpose of the Action",
  prompt: "The prompt to use to help in using the tool",
  tool: "ToolName",
}),
// ...
(is_answer_correct:Decision {
  id: "action",
  purpose: "The purpose of the decision",
  question: "The question to ask",
}),
... (N times)
// Structure declaration
(start)-[:NEXT]->(action),
// ...
(is_answer_correct)-[YES]->(next_step),
(is_answer_correct)-[NO]->(next_step),
(is_answer_correct)-[MAYBE]->(next_step), // You can use any number of output edges for decision nodes 
... (N times)
(action_n)-[:NEXT]->(end)
```

No NOT change the correct parts of the graph nor the graph and ONLY modify what is pointed by the errors
Make sure that the start and end nodes are correctly connected
"""
    input_graph: str = dspy.InputField(desc="The input graph")
    errors: str = dspy.InputField(desc="The errors to correct")
    graph: str = dspy.OutputField(desc="The corrected graph")
    
class NameAndDescriptionGenerator(dspy.Signature):
    graph: str = dspy.InputField(desc="The input")
    name: str = dspy.OutputField(desc="The snake case name of the cypher file (don't state that it is graph)")
    description: str = dspy.OutputField(desc="The task description (one phrase with just few words)")
    
class GraphProgramExtractor(dspy.Module):
    
    def __init__(
            self,
            lm: Optional[dspy.LM] = None,
            tools: List[Tool] = [],
            programs: GraphProgramList = GraphProgramList(),
        ):
        self.lm = lm
        self.extraction = dspy.Predict(GraphProgramExtractorSignature)
        self.graph_correction = dspy.ChainOfThought(CorrectGraphProgram)
        self.extract_name_and_description = dspy.Predict(NameAndDescriptionGenerator)
        self.cypher_parser = CypherOutputParser()
        tools_instructions = []
        for tool in tools:
            tools_instructions.append(f"- [{tool.name}]: {tool.description}")
        if tools_instructions:
            self.tools_instructions = "\n".join(tools_instructions)
        else:
            self.tools_instructions = "No tools provided"
        programs_instructions = []
        for program in programs.progs:
            programs_instructions.append(f"- [{program.name}]: {program.description}")
        if programs_instructions:
            self.programs_instructions = "\n".join(tools_instructions)
        else:
            self.programs_instructions = "No sub-routines provided"
        
    def forward(self, doc_or_docs: Union[Document, DocumentList]) -> GraphProgramList:
        if not isinstance(doc_or_docs, (Document, DocumentList)):
            raise ValueError(f"{type(self).__name__} input must be a Document or DocumentList")
        if isinstance(doc_or_docs, Document):
            documents = DocumentList()
            documents.docs = [doc_or_docs]
        else:
            documents = doc_or_docs
        result = GraphProgramList()
        for doc in tqdm(documents.docs):
            with dspy.context(lm=self.lm if self.lm is not None else dspy.settings.lm):
                pred = self.extraction(
                    document = doc.text,
                    tools = self.tools_instructions,
                    routines = self.programs_instructions,
                )
                pred.graph = self.cypher_parser.parse(pred.graph)
                graph = pred.graph
                pred = self.extract_name_and_description(
                    graph = f"```cypher\n{pred.graph}```"
                )
                name = pred.name
                description = pred.description
                graph_program = GraphProgram(name=name, description=description)
                for i in range(5):
                    try:
                        graph_program.from_cypher(graph)
                        graph_program.build()
                        break
                    except Exception as e:
                        pred = self.graph_correction(
                            input_graph = f"```cypher\n{graph}```",
                            errors = str(e),
                        )
                        pred.graph = self.cypher_parser.parse(pred.graph)
                        graph = pred.graph
                result.progs.append(graph_program)
        return result