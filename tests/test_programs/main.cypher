// @desc: The main program
CREATE
(start:Control {name:"Start"}),
(end:Control {name:"End"}),
(answer:Action {
    name:"Answer the objective's question",
    tool:"Speak",
    prompt:"You are an helpfull assistant, answer the given question"
}),
(start)-[:NEXT]->(answer),
(answer)-[:NEXT]->(end)