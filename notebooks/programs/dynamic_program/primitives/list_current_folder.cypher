// @desc: List the files inside the current folder
CREATE
(start:Control {name:"Start"}),
(end:Control {name:"End"}),
(list_folder:Action {
    name:"List the current directory",
    tool:"InternalShell",
    prompt:"ls",
    disable_inference:"true"
}),
(start)-[:NEXT]->(list_folder),
(list_folder)-[:NEXT]->(end)