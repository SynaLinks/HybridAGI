// @desc: Add entity or entities into the fact memory
CREATE
(start:Control {name:"Start"}),
(end:Control {name:"End"}),
(entity_add:Action {
    name: "Add entities to the fact memory based on the context",
    tool: "EntityAdd",
    prompt: "Use the content to add entities to the fact memory",
    disable_inference: "true"
}),
(start)-[:NEXT]->(entity_add),
(entity_add)-[:NEXT]->(end)