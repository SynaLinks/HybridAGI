// @desc: Display the given directory tree structure
CREATE
(start:Control {name:"Start"}),
(end:Control {name:"End"}),
(display_tree:Action {
    name:"Display the given directory tree structure",
    tool:"InternalShell",
    prompt:"Use the tree command to display the tree structure of the given directory"
}),
(tell_user:Action {
    name:"Tell the user",
    tool:"Speak",
    prompt:"Tell to the user the result of the tree command"
}),
(start)-[:NEXT]->(display_tree),
(display_tree)-[:NEXT]->(tell_user),
(tell_user)-[:NEXT]->(end)