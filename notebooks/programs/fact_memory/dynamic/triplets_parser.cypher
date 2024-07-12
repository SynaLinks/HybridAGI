// @desc: Parse text into knowledge graph triplets
CREATE
(start:Control {name:"Start"}),
(end:Control {name:"End"}),
(triplets_parser:Action {
    name: "Create a knowledge graph triplets from the content",
    tool: "TripletParser",
    prompt: "Convert the content into knowledge graph triplets",
    output: "parsed_triplets"
}),
(critique_triplets:Action {
    name: "Critique the triplets parsed",
    tool: "Predict",
    prompt: "Use the context to critique the parsed triplets compared to the file content,
    are the triplets properly parsed ?
    can the assistant parse more triplets ?
    if everything is correct, just say that the answer is correct"
}),
(are_triplets_correct:Decision {
    name: "Check if all possible triplets have been parsed from the file content",
    question: "Is the answer correct? make sure the answer correspond"
}),
(tell_user:Action {
    name:"Tell the user",
    tool:"Speak",
    prompt:"Tell to the user the content of the parsed triplets, DO NOT add any other content to the output, just the content of the input
    \n\n{parsed_triplets}\n\n",
    inputs: ["parsed_triplets"]
}),
(start)-[:NEXT]->(triplets_parser),
(triplets_parser)-[:NEXT]->(critique_triplets),
(critique_triplets)-[:NEXT]->(are_triplets_correct),
(are_triplets_correct)-[:ERROR]->(triplets_parser),
(are_triplets_correct)-[:UNKNOWN]->(triplets_parser),
(are_triplets_correct)-[:CORRECT]->(tell_user),
(tell_user)-[:NEXT]->(end)
