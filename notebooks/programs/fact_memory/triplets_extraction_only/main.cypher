// @desc: The main program
CREATE
(start:Control {name:"Start"}),
(end:Control {name:"End"}),
(parse_triplets:Action {
    name: "Create a triplet based on the objective's statement",
    tool: "TripletParser",
    prompt: "Use the objective's statement to infer triplets, DO NOT repeat previously parsed triplets",
}),
(critique:Action {
    name: "Critique parsed triplets",
    tool: "Predict",
    prompt: "Critique the parsed triplets, if everything is correct, just say that the answer is correct"
}),
(is_answer_correct:Decision {
    name: "Check if the answer to the objective's statement is correct",
    question: "Is the answer correct?"
}),
(triplets_extracted:Decision {
    name:"Check if all possible triplets have been extracted from the objectve's statement",
    question: "Can we extract more triplets from the objective's statement ?"
}),
(action_search:Action {
    name: "Search past actions to answer the objective's question",
    tool: "PastActionSearch",
    disable_inference:"false",
    prompt: "Get triplets from past action messages"
}),
(combined_triplets:Action {
    name: "Create a combined list of triplets",
    tool: "Speak",
    prompt: "Use the above search parsed triplets to create a combined list of triplets"
}),
(start)-[:NEXT]->(parse_triplets),
(parse_triplets)-[:NEXT]->(triplets_extracted),
(triplets_extracted)-[:NO]->(parse_triplets),
(triplets_extracted)-[:MAYBE]->(parse_triplets),
(triplets_extracted)-[:UNKNOWN]->(parse_triplets),
(triplets_extracted)-[:YES]->(action_search),
(action_search)-[:NEXT]->(end)