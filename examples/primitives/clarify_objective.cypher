// @desc: Clarify the objective of the user by asking questions, starts by picking a question to ask, then check if there is more question to ask, if so it loop back to ask more question.
CREATE
(start:Control {name:"Start"}),
(end:Control {name:"End"}),
(is_anything_unclear:Decision {
    name:"Find out if there is anything unclear in the Objective", 
    question:"Is the Objective unclear?"
}),
(ask_question:Program {
    name:"Pick one question to clarify the Objective",
    program:"ask_user"
}),
(refine_objective:Program {
    name:"Refine the objective",
    program:"update_objective"
}),
(start)-[:NEXT]->(is_anything_unclear),
(ask_question)-[:NEXT]->(refine_objective),
(refine_objective)-[:NEXT]->(is_anything_unclear),
// Decisions can have multiple arbitrary outcomes
(is_anything_unclear)-[:YES]->(ask_question),
(is_anything_unclear)-[:NO]->(end)