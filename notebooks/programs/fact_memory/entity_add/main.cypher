// @desc: The main program
CREATE
(start:Control {name:"Start"}),
(end:Control {name:"End"}),
(parse_triplets:Action {
    name: "Create a triplet based on the objective's statement",
    tool: "TripletParser",
    prompt: "Use the objective's statement to infer triplets",
    output: "triplets"
}),
(triplets_extracted:Decision {
    name:"Check if all possible triplets have been extracted from the objectve's statement",
    question: "Can we extract more triplets from the objective's statement ?"
}),
(entity_add:Action {
    name: "Create a fact memory entity based on the triplets parsed",
    tool: "EntityAdd",
    prompt: "Add the following triplets to the fact memory
    {triplets}
    ",
    disable_inference:"false",
    inputs: ["triplets"]
}),
(entities_added:Decision {
    name:"Check if entities were successfully added",
    question:"Were entitites in the form of triplets successfully added to the fact memory ?"
}),
(start)-[:NEXT]->(parse_triplets),
(parse_triplets)-[:NEXT]->(triplets_extracted),
(triplets_extracted)-[:NO]->(parse_triplets),
(triplets_extracted)-[:MAYBE]->(parse_triplets),
(triplets_extracted)-[:UNKNOWN]->(parse_triplets),
(triplets_extracted)-[:YES]->(entity_add),
(entity_add)-[:NEXT]->(entities_added),
(entities_added)-[:NO]->(triplets_extracted),
(entities_added)-[:MAYBE]->(triplets_extracted),
(entities_added)-[:UNKNOWN]->(triplets_extracted),
(entities_added)-[:YES]->(end)