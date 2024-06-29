// @desc: Print the current working directory
CREATE
(start:Control {name:"Start"}),
(end:Control {name:"End"}),
(pwd:Action {
    name:"Print the current working directory",
    tool:"InternalShell",
    prompt:"pwd",
    disable_inference:"true"
}),
(start)-[:NEXT]->(pwd),
(pwd)-[:NEXT]->(end)