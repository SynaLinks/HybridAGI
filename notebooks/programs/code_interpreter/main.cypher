// @desc: The main program
CREATE
(start:Control {name:"Start"}),
(end:Control {name:"End"}),
(plan_simulation:Action {
    name: "Plannify how to implement the code to answer the objective's question",
    tool: "Predict",
    prompt: "Explain what to code to answer the objective's question.
Make sure that your program answer the correct question from the objective.
First lay down the equations needed and explain your methodology"
}),
(simulate:Action {
    name: "Implement the code to answer's the objective question",
    tool: "CodeInterpreter",
    prompt: "Give me the python code to answer the objective's question.
Make sure that your program answer the correct question from the objective
Ensure that the corresponding libraries are loaded beforehand"
}),
(is_simulation_correct:Decision {
    name: "Check if the simulation is correct",
    question: "Is the simulation correct? Meaning no error/bug"
}),
(critique:Action {
    name: "Critique the code",
    tool: "Predict",
    prompt: "Critique the code, if no bug, just say that the code is correct"
}),
(answer:Action {
    name: "Answer the objective's question",
    tool: "Speak",
    prompt: "Answer the objective's question using the context's simulation output"
}),
(is_answer_correct:Decision {
    name: "Check if the answer to the objective's question is correct",
    question: "Is the answer correct? make sure the answer correspond"
}),
(start)-[:NEXT]->(plan_simulation),
(plan_simulation)-[:NEXT]->(simulate),
(simulate)-[:NEXT]->(critique),
(critique)-[:NEXT]->(is_simulation_correct),
(is_simulation_correct)-[:ERROR]->(simulate),
(is_simulation_correct)-[:UNKNOWN]->(simulate),
(is_simulation_correct)-[:CORRECT]->(answer),
(answer)-[:NEXT]->(end)