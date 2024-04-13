// @desc: Write text into files and try again if not successful
CREATE
(start:Control {name:"Start"}),
(end:Control {name:"End"}),
(write_files:Action {
    name:"Write a file into memory",
    tool:"WriteFile",
    prompt:"Use the context to infer the content of the file.
Use the context to infer the snake case or camel case filename.
Please always ensure to correctly infer the content of the file, don't be lazy."}),
(is_successfully_written:Decision {
    name:"Check if the files have been successfully written",
    question:"Are the files successfully written?"}),
(try_again:Action {
    name:"Correct and try again", 
    tool:"WriteFile",
    prompt:"Use the context to infer the content of the file.
Use the context to infer the snake case or camel case filename.
Please always ensure to correctly infer the content of the file, don't be lazy."}),
(start)-[:NEXT]->(write_files),
(write_files)-[:NEXT]->(is_successfully_written),
(try_again)-[:NEXT]->(is_successfully_written),
(is_successfully_written)-[:NO]->(try_again),
(is_successfully_written)-[:YES]->(end)