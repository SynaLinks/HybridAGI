// @desc: The main program
CREATE
(start:Control {name:"Start"}),
(end:Control {name:"End"}),
(read_file:Action {
    name:"Read a chunk of the given file",
    tool:"ReadFile",
    prompt:"The path of the file to read",
    output:"file_content"
}),
(is_eof:Decision {
    name:"Check if finished reading the file",
    question:"Is the file finished (meaning no [...] is present at the end)?"
}),
(parse_triplets:Action {
    name: "Create a triplet based on the objective's statement",
    tool: "TripletParser",
    prompt: "Use the the input content to infer triplets, DO NOT repeat previously parsed triplets
    {file_content}",
    inputs: ["file_content"]
}),
(triplets_extracted:Decision {
    name:"Check if all possible triplets have been extracted from the input content",
    question: "Can we extract more triplets from the input content ?"
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
(start)-[:NEXT]->(read_file),
(read_file)-[:NEXT]->(is_eof),
(is_eof)-[:NO]->(read_file),
(is_eof)-[:YES]->(parse_triplets),
(parse_triplets)-[:NEXT]->(triplets_extracted),
(triplets_extracted)-[:NO]->(parse_triplets),
(triplets_extracted)-[:MAYBE]->(parse_triplets),
(triplets_extracted)-[:UNKNOWN]->(parse_triplets),
(triplets_extracted)-[:YES]->(end)