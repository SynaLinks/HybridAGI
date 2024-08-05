// @desc: Tell a joke to the user
CREATE
// Nodes declaration
(start:Control {id: "start"}),
(end:Control {id: "end"}),
(tell_joke:Action {
  id: "tell_joke",
  purpose: "Tell a joke",
  tool: "Speak",
  prompt: "Imagine that you are the best comedian on earth, please tell your best joke"
}),
// Structure declaration
(start)-[:NEXT]->(tell_joke),
(tell_joke)-[:NEXT]->(end)