// @desc: Display the current directory tree structure
CREATE
(start:Control {name:"Start"}),
(end:Control {name:"End"}),
(display_tree:Action {
    name:"Display the current directory tree structure",
    tool:"InternalShell",
    prompt:"tree",
    disable_inference:"true"
}),
(tell_user:Action {
    name:"Tell the user",
    tool:"Speak",
    prompt:"Tell to the user the result of the tree command"
}),
(start)-[:NEXT]->(display_tree),
(display_tree)-[:NEXT]->(tell_user),
(tell_user)-[:NEXT]->(end)