// @desc: The main program
CREATE
(start:Control {name:"Start"}),
(end:Control {name:"End"}),
(start)-[:NEXT]->(end)