// @desc: Speak to the User
CREATE
(start:Control {name:"Start"}),
(end:Control {name:"End"}),
(speak:Action {
    name:"Speak to the User",
    tool:"Speak",
    prompt:"What you want to say"}),
(start)-[:NEXT]->(speak),
(speak)-[:NEXT]->(end)