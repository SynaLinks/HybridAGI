// @desc: Search for information and answer
CREATE
// Nodes declaration
(start:Control {id: "start"}),
(end:Control {id: "end"}),
(document_search:Action {
  id: "document_search",
  purpose: "Find relevant documents",
  tool: "DocumentSearch",
  prompt: "Please infer the similarity search query (only ONE item) based on the Objective's question"
}),
(answer:Action {
  id: "answer",
  purpose: "Answer the Objective's question",
  tool: "Speak",
  prompt: "\nPlease answer the Objective's question using the relevant documents in your context.\nIf no document are relevant just say that you don't know.\nDon't state the Objective's question and only give the correct answer.\n"
}),
// Structure declaration
(start)-[:NEXT]->(document_search),
(document_search)-[:NEXT]->(answer),
(answer)-[:NEXT]->(end)