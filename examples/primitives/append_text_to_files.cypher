// @desc: Append text into files and try again if not successful
CREATE
(start:Control {name:"Start"}),
(end:Control {name:"End"}),
(append_files:Action {
    name:"Try to append files into memory",
    tool:"AppendFiles",
    prompt:"Use the context to infer the content of the file.
Use the context to infer the snake case or camel case filename.
Please always ensure to correctly infer the content of the file, don't be lazy."}),
(start)-[:NEXT]->(append_files),
(append_files)-[:NEXT]->(end)