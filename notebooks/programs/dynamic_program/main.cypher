// @desc: The main program
CREATE
(start:Control {name:"Start"}),
(end:Control {name:"End"}),
(fulfill_objective:Program {
    name: "Fulfill the objective",
    program: "fulfill_objective"
}),
(start)-[:NEXT]->(fulfill_objective),
(fulfill_objective)-[:NEXT]->(end)