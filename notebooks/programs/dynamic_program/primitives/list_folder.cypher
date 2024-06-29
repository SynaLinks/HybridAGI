// @desc: List the files inside the given folder
CREATE
(start:Control {name:"Start"}),
(end:Control {name:"End"}),
(list_folder:Action {
    name:"List the given directory",
    tool:"InternalShell",
    prompt:"Give ONLY the unix command ls to list the given directory without any additional details"
}),
(tell_user:Action {
    name:"Tell the context of the folder to the User",
    tool:"Speak",
    prompt:"Tell the content of the folder to the user, if empty just say the folder is empty"
}),
(start)-[:NEXT]->(list_folder),
(list_folder)-[:NEXT]->(tell_user),
(tell_user)-[:NEXT]->(end)