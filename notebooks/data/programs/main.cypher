// @desc: The main program
CREATE
// Nodes declaration
(start:Control {id: "start"}),
(end:Control {id: "end"}),
(fulfill_objective:Program {
  id: "fulfill_objective",
  purpose: "Fulfill the objective",
  program: "fulfill_objective"
}),
// Structure declaration
(start)-[:NEXT]->(fulfill_objective),
(fulfill_objective)-[:NEXT]->(end)