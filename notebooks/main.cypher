// @desc: The main program
CREATE
// Nodes declaration
(start:Control {id: "start"}),
(end:Control {id: "end"}),
(answer:Action {
  id: "answer",
  purpose: "Answer the user question",
  tool: "Speak",
  prompt: "Please answer to the Objective's question"
}),
// Structure declaration
(start)-[:NEXT]->(answer),
(answer)-[:NEXT]->(end)