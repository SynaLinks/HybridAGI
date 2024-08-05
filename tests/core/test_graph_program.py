import hybridagi.core.graph_program as gp

def test_graph_program_empty():
    main=gp.GraphProgram(
        name="main",
        description="The main program",
    )

def test_one_action_program():
    main = gp.GraphProgram(
        name="main",
        description="The main program",
    )
    
    main.add(gp.Action(
        id = "answer",
        purpose = "Answer the Objective's question",
        tool = "Speak",
        prompt = "Please answer to the Objective's question",
    ))

    main.connect("start", "answer")
    main.connect("answer", "end")
    
    main.build()
    
    cypher = main.to_cypher()
    assert cypher == \
r"""// @desc: The main program
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
(answer)-[:NEXT]->(end)"""

def test_from_cypher():
    cypher = \
r"""// @desc: The main program
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
(answer)-[:NEXT]->(end)"""

    main = gp.GraphProgram("main").from_cypher(cypher)
    assert main.to_cypher() == cypher
    
    
def test_one_action_one_decision_program():
    main=gp.GraphProgram(name="main", description="The main program")
    
    main.add(gp.Decision(
        id = "is_objective_unclear",
        purpose = "Check if the Objective is unclear",
        question="Is the Objective's question still unclear?",
    ))
    
    main.add(gp.Action(
        id = "clarify",
        purpose = "Ask one question to clarify the Objective",
        tool = "AskUser",
        prompt = "Pick one question to clarify the Objective's question",
    ))
    
    main.add(gp.Action(
        id = "refine_objective",
        purpose = "Refine the Objective's question",
        tool = "UpdateObjective",
        prompt = "Please refine the Objective's question",
    ))
    
    main.add(gp.Action(
        id = "answer",
        purpose = "Answer the Objective's question",
        tool = "Speak",
        prompt = "Please answer to the Objective's question",
    ))
    
    main.connect("start", "is_objective_unclear")
    main.connect("is_objective_unclear", "clarify", label="Clarify")
    main.connect("is_objective_unclear", "answer", label="Answer")
    main.connect("clarify", "refine_objective")
    main.connect("refine_objective", "answer")
    main.connect("answer", "end")
    
    main.build()
    
    assert main.get_decision_choices("is_objective_unclear") == ["CLARIFY", "ANSWER"]
    
    cypher = main.to_cypher()
    
    assert cypher == \
"""// @desc: The main program
CREATE
// Nodes declaration
(start:Control {id: "start"}),
(end:Control {id: "end"}),
(is_objective_unclear:Decision {
  id: "is_objective_unclear",
  purpose: "Check if the Objective is unclear",
  question: "Is the Objective's question still unclear?"
}),
(clarify:Action {
  id: "clarify",
  purpose: "Ask one question to clarify the Objective",
  tool: "AskUser",
  prompt: "Pick one question to clarify the Objective's question"
}),
(refine_objective:Action {
  id: "refine_objective",
  purpose: "Refine the Objective's question",
  tool: "UpdateObjective",
  prompt: "Please refine the Objective's question"
}),
(answer:Action {
  id: "answer",
  purpose: "Answer the Objective's question",
  tool: "Speak",
  prompt: "Please answer to the Objective's question"
}),
// Structure declaration
(start)-[:NEXT]->(is_objective_unclear),
(is_objective_unclear)-[:CLARIFY]->(clarify),
(is_objective_unclear)-[:ANSWER]->(answer),
(clarify)-[:NEXT]->(refine_objective),
(refine_objective)-[:NEXT]->(answer),
(answer)-[:NEXT]->(end)"""