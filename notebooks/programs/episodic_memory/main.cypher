// @desc: The main program
CREATE
(start:Control {name:"Start"}),
(end:Control {name:"End"}),
(action_search:Action {
    name: "Search past actions to answer the objective's question",
    tool: "PastActionSearch",
    prompt: "Use the objective's question to infer the search query"
}),
(is_answer_known:Decision {
    name:"Check if the answer to the objective's question is present in the previous actions search",
    question: "Is the answer in the previous search? if the answer is not present or not relevant select websearch otherwise select answer"
}),
(websearch:Action {
    name: "Perform a duckduckgo search",
    tool: "DuckDuckGoSearch",
    prompt: "Use the objective's question to infer the search query"
}),
(answer:Action {
    name: "Answer the objective's question based on the search",
    tool: "Speak",
    prompt: "Use the above search to infer the answer, without saying that it is based on your past actions"
}),
(start)-[:NEXT]->(action_search),
(action_search)-[:NEXT]->(is_answer_known),
(is_answer_known)-[:ANSWER]->(answer),
(is_answer_known)-[:WEB_SEARCH]->(websearch),
(websearch)-[:NEXT]->(answer),
(answer)-[:NEXT]->(end)