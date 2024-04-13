// @desc: Search the answer to the given question on internet
CREATE
(start:Control {name:"Start"}),
(end:Control {name:"End"}),
(internet_search:Action {
    name:"Search for answer on Internet",
    tool:"InternetSearch",
    prompt:"Ask the question to answer"}),
(start)-[:NEXT]->(internet_search),
(internet_search)-[:NEXT]->(end)