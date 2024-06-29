// @desc: Ask information to the User
CREATE
(start:Control {name:"Start"}),
(end:Control {name:"End"}),
(ask_user:Action {
    name:"Ask the User about the information",
    tool:"AskUser",
    prompt:"Please ask the User in a formal way"}),
(start)-[:NEXT]->(ask_user),
(ask_user)-[:NEXT]->(end)