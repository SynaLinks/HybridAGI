// @desc: List the files inside the given folder
CREATE
(start:Control {name:"Start"}),
(end:Control {name:"End"}),
(list_folder:Action {
    name:"List the given directory",
    tool:"InternalShell",
    prompt:"Give ONLY the unix command ls to list the given directory without any additional details"}),
(start)-[:NEXT]->(list_folder),
(list_folder)-[:NEXT]->(end)