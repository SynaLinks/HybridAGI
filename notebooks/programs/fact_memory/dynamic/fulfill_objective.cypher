// @desc: Try to call an existing program to fulfill the objective
CREATE
(start:Control {name:"Start"}),
(end:Control {name:"End"}),
(program_search:Action {
    name:"Search for existing routine to fulfill the objective", 
    tool:"ProgramSearch",
    prompt:"Use the objective to describe in ONE short sentence the action to take"
}),
(is_program_known:Decision {
    name: "Check if the routine to fulfill the objective is in the previous search",
    question: "Is the routine to fulfill the objective in the above search? If you don't know consider the most probable"
}),
(call_program:Action {
    name:"Pick the most appropriate routine from the previous search", 
    tool:"CallProgram",
    prompt:"Use the context to known which program to pick. Only infer the name of the program without addtionnal details. Make sure to give only the name of the routine."
}),
(start)-[:NEXT]->(program_search),
(program_search)-[:NEXT]->(is_program_known),
(is_program_known)-[:YES]->(call_program),
(is_program_known)-[:MAYBE]->(call_program),
(is_program_known)-[:NO]->(end),
(call_program)-[:NEXT]->(end)