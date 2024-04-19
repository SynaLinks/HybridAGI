// @desc: Write text into a files
CREATE
(start:Control {name:"Start"}),
(end:Control {name:"End"}),
(write_file:Action {
    name:"Write a file into memory",
    tool:"WriteFile",
    prompt:"Use the context to infer the content of the file.
Use the context to infer the snake case or camel case filename.
Never assume anything and do what you was asked for.
Please always ensure to correctly infer the content of the file without additonal information, don't be lazy."}),
(start)-[:NEXT]->(write_file),
(write_file)-[:NEXT]->(end)