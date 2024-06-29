// @desc: The main program
CREATE
(start:Control {name:"Start"}),
(end:Control {name:"End"}),
(intro:Action {
    name: "Write the introduction for a news article on the objective's topic",
    tool: "Predict",
    prompt: "Imagine that you are a programming blog writter, please give me an appealing introduction
The introduction should present the company and its objectives",
    output: "introduction"
}),
(first_paragraph:Action {
    name: "Write the first paragraph for a news article on the objective's topic",
    tool: "Predict",
    prompt: "Imagine that you are a programming blog writter, please give me an appealing first paragraph
Don't state that it is the first paragraph
The first paragraph would introduce the technology and present the DSL",
    output: "first_paragraph"
}),
(second_paragraph:Action {
    name: "Write the second paragraph for a news article on the objective's topic",
    tool: "Predict",
    prompt: "Imagine that you are a news writter, please give me an appealing second paragraph
The second paragraph explain the technology",
    output: "second_paragraph"
}),
(third_paragraph:Action {
    name: "Write the third paragraph for a news article on the objective's topic",
    tool: "Predict",
    prompt: "Imagine that you are a news writter,
Please give me an appealing third paragraph. 
The third paragraph should talk about potentials applications",
    output: "third_paragraph"
}),
(conclusion:Action {
    name: "Write the conclusion",
    tool: "Predict",
    prompt: "Imagine that you are a news writter, please give me an appealing conclusion for the following draft:

{introduction}
{first_paragraph}
{second_paragraph}
{third_paragraph}

Don't state that it is the conclusion",
    inputs: ["introduction", "first_paragraph", "second_paragraph", "third_paragraph"],
    output: "conclusion"
}),
(add_title_and_sections:Action {
    name: "Write the final version of the article in markdown format",
    tool: "Speak",
    prompt: "Format the following draft into markdown format

{introduction}
{first_paragraph}
{second_paragraph}
{third_paragraph}
{conclusion}

Ensure to cleanup the above draft and format it in markdown format
Don't apologies or explain yourself, only answer with the final article.",
    inputs: ["introduction", "first_paragraph", "second_paragraph", "third_paragraph", "conclusion"]
}),
(start)-[:NEXT]->(intro),
(intro)-[:NEXT]->(first_paragraph),
(first_paragraph)-[:NEXT]->(second_paragraph),
(second_paragraph)-[:NEXT]->(third_paragraph),
(third_paragraph)-[:NEXT]->(conclusion),
(conclusion)-[:NEXT]->(add_title_and_sections),
(add_title_and_sections)-[:NEXT]->(end)