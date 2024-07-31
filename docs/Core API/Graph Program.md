The Graph Programs are a special data type representing a workflow of actions and decisions with calls to other programs. They are used by our own custom Agent, the `GraphProgramInterpreter`. In order help you to build them, we provide two ways of doing it: Using Python or Cypher.

The two ways are equivalent and allows you to choose the one you prefer.

### Python Usage:

```python
import hybridagi.core.graph_program as gp

main = gp.GraphProgram(
	id = "main",
	desc = "The main program",
)

main.add("answer", gp.Action(
	tool = "Speak"
	purpose = ""
	prompt = \
"""
Please answer to the following question: 
{{objective}}
"""
	inputs=["objective"],
	ouput="answer",
))

main.connect("start", "answer")
main.connect("answer", "end")

```

### Building your program

To perform a formal verification of the graph data we provide a way to build your `GraphProgram` ensuring that the data flow is correct. If some inconsistency is detected it will raise an error. For the above program you just have to do:

```python

main.build()

```

This operation will check that there no orphan nodes in your graph (nodes connected to any nodes), as well as checking that each node is reachable from the `start` and `end` nodes.

## Using decision-making steps

Decision making steps allow the Agent to branch over different paths in a program, like conditions in traditional programming, it allow conditional loops and multi-output decisions.

```python
import hybridagi.core.graph_program as gp

main=gp.GraphProgram(name="main", description="The main program")
    
main.add("is_objective_unclear", gp.Decision(
	purpose="Check if the question needs clarification or not",
	prompt="Is the following question unclear?\n{{question}}",
	inputs=["objective"],
))

main.add("clarify", gp.Action(
	purpose="Ask one question to clarify the user's objective",
	tool="AskUser",
	prompt="Please pick one question to clarify the following: {{objective}}",
	inputs=["objective"],
	output="clarification"
))

main.add("answer", gp.Action(
	purpose="Answer the question",
	tool="Speak",
	prompt="Please answer to the following question: {{objective}}",
	inputs=["objective"],
))

main.add("refine_objective", gp.Action(
	purpose="Refine the objective",
	tool="Predict",
	prompt= \
"""You asked the following question:
Question: {{clarification}}

Please refine the following objective:
Objective: {{objective}}""",
        inputs=["objective", "clarification"],
        output="objective"
    ))
    
main.connect("start", "is_objective_unclear")
main.connect("is_objective_unclear", "clarify", label="Clarify")
main.connect("is_objective_unclear", "answer", label="Answer")
main.connect("clarify", "refine_objective")
main.connect("refine_objective", "answer")
main.connect("answer", "end")

main.build()

```

## Using sub-programs

 TODO

### Loading from Cypher

```python

cypher == \
r"""// @desc: The main program
CREATE
// Nodes declaration
(start:Control {purpose: "Start"}),
(end:Control {purpose: "End"}),
(is_objective_unclear:Decision {
  purpose: "is_objective_unclear",
  prompt: "Is the following question unclear?\n{{question}}",
  inputs: [
    "objective"
  ]
}),
(clarify:Action {
  purpose: "Ask one question to clarify the user's objective",
  tool: "AskUser",
  prompt: "Please pick one question to clarify the following: {{objective}}",
  inputs: [
    "objective"
  ],
  output: "clarification"
}),
(answer:Action {
  purpose: "Answer the question",
  tool: "Speak",
  prompt: "Please answer to the following question: {{objective}}",
  inputs: [
    "objective"
  ]
}),
(refine_objective:Action {
  purpose: "Refine the objective",
  tool: "Predict",
  prompt: "You asked the following question:\nQuestion: {{clarification}}\n\nPlease refine the following objective:\nObjective: {{objective}}",
  inputs: [
    "objective",
    "clarification"
  ],
  output: "objective"
}),
// Structure declaration
(start)-[:NEXT]->(is_objective_unclear),
(is_objective_unclear)-[:CLARIFY]->(clarify),
(is_objective_unclear)-[:ANSWER]->(answer),
(clarify)-[:NEXT]->(refine_objective),
(refine_objective)-[:NEXT]->(answer),
(answer)-[:NEXT]->(end)"""

main = gp.GraphProgram().from_cypher(cypher)

```
