# Graph Program

The Graph Programs are a special data type representing a workflow of actions and decisions with calls to other programs. They are used by our own custom Agent, in order help you to build them, we provide two ways of doing it: Using Python or Cypher.

The two ways are equivalent and allows you to choose the one you prefer, we recommend you however to use the pythonic way, to avoid syntax errors, and eventually save them into Cypher format for later use.

## Python Usage

```python
import hybridagi.core.graph_program as gp

main = gp.GraphProgram(
	name = "main",
	description = "The main program",
)

main.add("answer", gp.Action(
	tool = "Speak",
	purpose = "Answer the Objective's question",
	prompt = "Please answer to the Objective's question",
))

main.connect("start", "answer")
main.connect("answer", "end")

```

## Building your program

To perform a formal verification of the graph data we provide a way to build your `GraphProgram` ensuring that the data flow is correct. If some inconsistency is detected it will raise an error. For the above program you just have to do:

```python
main.build()
```

This operation will check that there no orphan nodes in your graph (nodes connected to any nodes), as well as checking that each node is reachable from the `start` and `end` nodes.

Although we verify the structure of the program, we cannot verify if the name of tool used is accurate or if the program referenced is correct outside of the execution environment. This implies that you should be cautious in using the appropriate names, otherwise, the interpreter Agent will generate an error when it encounters the problematic step.

## Using decision-making steps

Decision making steps allow the Agent to branch over different paths in a program, like conditions in traditional programming, it allow conditional loops and multi-output decisions.

```python
import hybridagi.core.graph_program as gp

main = gp.GraphProgram(
    name="main",
    description="The main program",
)
    
main.add(gp.Decision(
    id="is_objective_unclear",
    purpose="Check if the Objective's is unclear",
    question="Is the Objective's question unclear?",
))

main.add(gp.Action(
    id="clarify",
    purpose="Ask one question to clarify the user's Objective",
    tool="AskUser",
    prompt="Please pick one question to clarify the Objective's question",
))

main.add(gp.Action(
    id="answer",
    purpose="Answer the question",
    tool="Speak",
    prompt="Please answer to the Objective's question",
))
    
main.add(gp.Action(
    id="refine_objective",
    purpose="Refine the objective",
    tool="UpdateObjective",
    prompt="Please refine the user Objective",
))
    
main.connect("start", "is_objective_unclear")
main.connect("is_objective_unclear", "clarify", label="Clarify")
main.connect("is_objective_unclear", "answer", label="Answer")
main.connect("clarify", "refine_objective")
main.connect("refine_objective", "answer")
main.connect("answer", "end")

main.build()
```

## Using Program calls

```python
import hybridagi.core.graph_program as gp

clarify_objective = gp.GraphProgram(
    name="clarify_objective",
    description="Clarify the objective by asking question to the user",
)

clarify_objective.add(gp.Decision(
    id = "is_anything_unclear",
    purpose = "Check if the Objective is unclear",
    question = "Is the Objective still unclear?",
))

clarify_objective.add(gp.Action(
    id = "clarify",
    purpose = "Ask question to clarify the user request",
    tool = "AskUser",
    prompt = "Pick one question to clarify the Objective",
))

clarify_objective.add(gp.Action(
    id = "refine_objective",
    purpose = "Refine the question",
    tool = "UpdateObjective",
    prompt = "Refine the Objective",
))

clarify_objective.connect("start", "is_anything_unclear")
clarify_objective.connect("is_anything_unclear", "clarify", label="Clarify")
clarify_objective.connect("is_anything_unclear", "end", label="Answer")
clarify_objective.connect("clarify", "refine_objective")
clarify_objective.connect("refine_objective", "end")

clarify_objective.build()

main = gp.GraphProgram(
    name="main",
    description="The main program",
)

main.add(gp.Program(
    id = "clarify_objective",
    purpose = "Clarify the user objective if needed",
    program = "clarify_objective"
))

main.add(gp.Action(
    id = "answer",
    purpose = "Answer the objective's question",
    tool = "Speak",
    prompt = "Answer the Objective's question",
))

main.connect("start", "clarify_objective")
main.connect("clarify_objective", "answer")
main.connect("answer", "end")

main.build()
```

## Loading from Cypher

```python
import hybridagi.core.graph_program as gp

cypher = \
"""
// @desc: The main program
CREATE
// Nodes declaration
(start:Control {id: "start"}),
(end:Control {id: "end"}),
(answer:Action {
  id: "answer",
  purpose: "Answer the Objective's question",
  tool: "Speak",
  prompt: "Please answer to the Objective's question"
}),
// Structure declaration
(start)-[:NEXT]->(answer),
(answer)-[:NEXT]->(end)
"""

main = gp.GraphProgram().from_cypher(cypher)

```

## Saving into a file

```python
# This command save the program into the corresponding folder
main.save("programs/")
```

## Loading from a file

```python
from hybridagi.readers import GraphProgramReader

reader = GraphProgramReader()

main = reader("main.cypher")
```
