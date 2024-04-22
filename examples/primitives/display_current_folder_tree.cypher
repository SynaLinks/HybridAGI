// @desc: Display the current directory tree structure
CREATE
(start:Control {name:"Start"}),
(end:Control {name:"End"}),
(display_tree:Action {
    name:"Display the current directory tree structure",
    tool:"InternalShell",
    prompt:"tree",
    disable_inference:"true"}),
(start)-[:NEXT]->(display_tree),
(display_tree)-[:NEXT]->(end)