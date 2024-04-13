// @desc: Upload the given file or folder to the User (creates a .zip archive)
CREATE
(start:Control {name:"Start"}),
(end:Control {name:"End"}),
(upload:Action {
    name:"Upload the given file or folder",
    tool:"Upload",
    prompt:"The file or folder to upload"}),
(start)-[:NEXT]->(upload),
(upload)-[:NEXT]->(end)