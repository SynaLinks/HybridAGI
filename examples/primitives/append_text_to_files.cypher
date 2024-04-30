// @desc: Append text into files and try again if not successful
CREATE
(start:Control {name:"Start"}),
(end:Control {name:"End"}),
(append_files:Action {
    name:"Try to append files into memory",
    tool:"AppendFiles",
    prompt:"Use the context to infer the correct filename to append.
Make sure to use the appropriate file extension.
Use the context and objective to infer the content of the file.
Avoid any placeholder in the content of the file."}),
(start)-[:NEXT]->(append_files),
(append_files)-[:NEXT]->(end)