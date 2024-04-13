// @desc: Upload to the user the current working directory
CREATE
(start:Control {name:"Start"}),
(end:Control {name:"End"}),
(upload_current_folder:Action {
    name:"Upload the current working directory",
    tool:"Upload",
    prompt:".",
    disable_inference:"true"}),
(start)-[:NEXT]->(upload_current_folder),
(upload_current_folder)-[:NEXT]->(end)