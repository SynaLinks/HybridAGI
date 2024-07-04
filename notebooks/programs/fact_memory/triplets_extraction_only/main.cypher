// @desc: The main program
CREATE
(start:Control {name:"Start"}),
(end:Control {name:"End"}),
(parse_triplets:Action {
    name: "Create a list of triplets based on the objective's statement",
    tool: "TripletParser",
    prompt: "Use the objective's statement to extract a list of triplets",
    output: "triplets"
}),
(triplets_extracted:Decision {
    name:"Check if all possible triplets have been extracted from the objectve's statement",
    question: "Can we extract more triplets from the objective's statement ?"
}),
(speak:Action {
    name:"Enumerate the triplets extracted",
    tool:"Speak",
    prompt:"Enumerate the triplets extracted
    
    {triplets}",
    inputs: ["triplets"]
}),
(start)-[:NEXT]->(parse_triplets),
(parse_triplets)-[:NEXT]->(triplets_extracted),
(triplets_extracted)-[:NO]->(parse_triplets),
(triplets_extracted)-[:MAYBE]->(parse_triplets),
(triplets_extracted)-[:UNKNOWN]->(parse_triplets),
(triplets_extracted)-[:YES]->(end)