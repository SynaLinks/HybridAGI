import hybridagi.core.graph_program as gp

def test_graph_program_empty():
    main=gp.GraphProgram(name="main", description="The main program")

def test_one_action_program():
    main=gp.GraphProgram(name="main", description="The main program")
        
    main.add("answer", gp.Action(
        tool="Speak",
        purpose="Answer the given question",
        prompt="Please answer to the following question: {{question}}",
        inputs=["objective"],
    ))

    main.connect("start", "answer")
    main.connect("answer", "end")
    
    main.build()
    
    cypher=main.to_cypher()
    assert cypher == \
r"""// @desc: The main program
CREATE
// Nodes declaration
(start:Control {purpose: "Start"}),
(end:Control {purpose: "End"}),
(answer:Action {
  purpose: "Answer the given question",
  tool: "Speak",
  prompt: "Please answer to the following question: {{question}}",
  inputs: [
    "objective"
  ]
}),
// Structure declaration
(start)-[:NEXT]->(answer),
(answer)-[:NEXT]->(end)"""

def test_from_cypher():
    cypher = \
r"""// @desc: The main program
CREATE
// Nodes declaration
(start:Control {purpose: "Start"}),
(end:Control {purpose: "End"}),
(answer:Action {
  purpose: "Answer the given question",
  tool: "Speak",
  prompt: "Please answer to the following question: {{question}}",
  inputs: [
    "objective"
  ]
}),
// Structure declaration
(start)-[:NEXT]->(answer),
(answer)-[:NEXT]->(end)"""

    main = gp.GraphProgram().from_cypher(cypher)
    assert main.to_cypher() == cypher
    
    
def test_one_action_one_decision_program():
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
    
    cypher = main.to_cypher()
    
    assert cypher == \
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