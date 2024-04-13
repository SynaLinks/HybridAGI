// @desc: Perform a similarity based search on the filesystem
CREATE
(start:Control {name:"Start"}),
(end:Control {name:"End"}),
(content_search:Action {
    name:"Perform a similarity based search in the filesystem",
    tool:"ContentSearch",
    prompt:"Describe precisely what you are looking for"}),
(start)-[:NEXT]->(content_search),
(content_search)-[:NEXT]->(end)