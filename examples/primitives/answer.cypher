// @desc: Tell the answer to the User
CREATE
(start:Control {name:"Start"}),
(end:Control {name:"End"}),
(tell_answer:Action {
    name:"Tell the right answer to the User",
    tool:"Speak",
    prompt:"Please tell the answer based on the context.
Make sure to always give the best answer.
If you don't know, just say that you don't known."}),
(start)-[:NEXT]->(tell_answer),
(tell_answer)-[:NEXT]->(end)