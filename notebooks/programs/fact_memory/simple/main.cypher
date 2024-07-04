// @desc: The main program
CREATE
(start:Control {name:"Start"}),
(end:Control {name:"End"}),
(parse_triplets:Action {
    name:"Extract knowledge triplets from the objective's statement",
    tool:"Speak",
    prompt:"Use the objective's statement to create a list of knowledge triplets in the format ('subject', 'predicate', 'object'). DO NOT add any other content
    
    Example:
    London is the capital of England. Westminster is located in London.

    [
        ('Capital_of_England', 'is', 'London'),
        ('Location_of_Westminster', 'within', 'London'),
        ('Part_of_London', 'is', 'Westminster')
    ]"
}),
(triplets_extracted:Decision {
    name:"Check if all possible triplets have been extracted from the objectve's statement",
    question: "Can we extract more triplets from the objective's statement ?"
}),
(start)-[:NEXT]->(parse_triplets),
(parse_triplets)-[:NEXT]->(triplets_extracted),
(triplets_extracted)-[:NO]->(parse_triplets),
(triplets_extracted)-[:MAYBE]->(parse_triplets),
(triplets_extracted)-[:UNKNOWN]->(parse_triplets),
(triplets_extracted)-[:YES]->(end)