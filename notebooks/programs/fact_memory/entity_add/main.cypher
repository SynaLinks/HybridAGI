// @desc: The main program
CREATE
(start:Control {name:"Start"}),
(end:Control {name:"End"}),
(parse_triplets:Action {
    name: "Create a triplet based on the objective's statement",
    tool: "TripletParser",
    prompt: "Use the objective's statement to infer triplets, DO NOT repeat previously parsed triplets"
}),
(triplets_extracted:Decision {
    name:"Check if all possible triplets have been extracted from the objectve's statement",
    question: "Can we extract more triplets from the objective's statement ?"
}),
(action_search:Action {
    name: "Search past actions to answer the objective's question",
    tool: "PastActionSearch",
    disable_inference:"false",
    prompt: "Get all past action messages VERBATIM",
    output: "past_actions"
}),
(entity_add:Action {
    name: "Add entities to the fact memory based on past actions",
    tool: "EntityAdd",
    prompt: "Get all past action messages",
    disable_inference:"false"
}),
(start)-[:NEXT]->(parse_triplets),
(parse_triplets)-[:NEXT]->(triplets_extracted),
(triplets_extracted)-[:NO]->(parse_triplets),
(triplets_extracted)-[:MAYBE]->(parse_triplets),
(triplets_extracted)-[:UNKNOWN]->(parse_triplets),
(triplets_extracted)-[:YES]->(entity_add),
(entity_add)-[:NEXT]->(end)