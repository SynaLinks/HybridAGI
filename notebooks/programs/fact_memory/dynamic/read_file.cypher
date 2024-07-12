// @desc: Read the given document
CREATE
(start:Control {name:"Start"}),
(end:Control {name:"End"}),
(read_file:Action {
    name:"Read a chunk of the given file",
    tool:"ReadFile",
    prompt:"The path of the file to read"
}),
(tell_user:Action {
    name:"Tell the user",
    tool:"Speak",
    prompt:"Tell to the user the content of the read file, DO NOT add any other content to the output, DO NOT add file metadata, just the content of the file"
}),
(start)-[:NEXT]->(read_file),
(read_file)-[:NEXT]->(tell_user),
(tell_user)-[:NEXT]->(end)