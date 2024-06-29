// @desc: Try to create the given folder, notify the user of the success
CREATE
(start:Control {name:"Start"}),
(end:Control {name:"End"}),
(create_folder:Action {
    name:"Try to create the folder",
    tool:"InternalShell",
    prompt:"Give ONLY the unix mkdir command to create the folder without any additional details"}),
(is_successfully_created:Decision {
    name:"Check if the folder have been created", 
    question:"Have the folder been successfully created?"}),
(notify_success:Action {
    name:"Notify the folder creation",
    tool:"Speak",
    prompt:"Folder successfully created",
    disable_inference:"true"
}),
(notify_failure:Action {
    name:"Tell the User why it failed",
    tool:"Speak",
    prompt:"Please tell the User the reason why the folder coudn't be created based on the above trace.
Your answer you be short an concise."}),
(start)-[:NEXT]->(create_folder),
(create_folder)-[:NEXT]->(is_successfully_created),
(is_successfully_created)-[:YES]->(notify_success),
(is_successfully_created)-[:NO]->(notify_failure),
(notify_success)-[:NEXT]->(end),
(notify_failure)-[:NEXT]->(end)