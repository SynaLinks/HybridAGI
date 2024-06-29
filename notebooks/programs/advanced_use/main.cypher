// @desc: The main program
CREATE
(start:Control {name:"Start"}),
(end:Control {name:"End"}),
(document_search:Action {
    name: "Search to information to answer the objective's question",
    tool: "DocumentSearch",
    prompt: "Use the objective's question to infer the search query"
}),
(answer:Action {
    name: "Answer the objective's question",
    tool: "Predict",
    prompt: "You are an helpfull assistant, answer the given question using the above search"
}),
(start)-[:NEXT]->(document_search),
(document_search)-[:NEXT]->(answer),
(answer)-[:NEXT]->(end)