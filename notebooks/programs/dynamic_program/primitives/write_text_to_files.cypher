// @desc: Write text into a files
CREATE
(start:Control {name:"Start"}),
(end:Control {name:"End"}),
(write_file:Action {
    name:"Write a file into memory",
    tool:"WriteFile",
    prompt:"Use the context to infer the snake case or camel case filename.
Make sure to use the appropriate file extension based on the content of the file.
Use the context and objective to infer the content of the file.
Avoid any placeholder in the content of the file.
Make sure to respect the case"
}),
(start)-[:NEXT]->(write_file),
(write_file)-[:NEXT]->(end)