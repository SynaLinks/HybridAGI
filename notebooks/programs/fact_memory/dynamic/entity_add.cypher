// @desc: Add entity or entities into the fact memory
CREATE
(start:Control {name:"Start"}),
(end:Control {name:"End"}),
(entity_add:Action {
    name: "Add entities to the fact memory based on the objective",
    tool: "EntityAdd",
    prompt: "Use the objective to add entities to the fact memory",
    disable_inference: "true"
}),
(start)-[:NEXT]->(entity_add),
(entity_add)-[:NEXT]->(end)