// @desc: Read the given document to answer the given question
CREATE
(start:Control {name:"Start"}),
(end:Control {name:"End"}),
(read_file:Action {
    name:"Read a chunk of the given file",
    tool:"ReadFile",
    prompt:"The path of the file to read"}),
(is_eof:Decision {
    name:"Check if finished reading the file",
    question:"Is the file finished (meaning no [...] is present at the end)?"}),
(is_answer_known:Decision {
    name:"Check if the Answer is known", 
    question:"Do you known the Answer to the Objective question based on the above information?"}),
(tell_answer:Action {
    name:"Answer the given question",
    tool:"Speak",
    prompt:"Answer the Objective question based on the above search
If the answer is not found, just say the answer is not found in this document."}),
(start)-[:NEXT]->(read_file),
(read_file)-[:NEXT]->(is_eof),
(is_eof)-[:YES]->(tell_answer),
(is_eof)-[:NO]->(read_file),
(is_answer_known)-[:YES]->(tell_answer),
(is_answer_known)-[:NO]->(read_file),
(tell_answer)-[:NEXT]->(end)