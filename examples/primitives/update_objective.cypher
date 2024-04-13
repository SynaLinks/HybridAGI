// @desc: Update the objective
CREATE
(start:Control {name:"Start"}),
(end:Control {name:"End"}),
(update_objective:Action {
    name:"Update the new long-term objective",
    tool:"UpdateObjective",
    prompt:"The new objective"}),
(start)-[:NEXT]->(update_objective),
(update_objective)-[:NEXT]->(end)