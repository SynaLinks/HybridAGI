"""The prompts for extracting graph as Cypher. Copyright (C) 2023 SynaLinks. License: GPL-3.0"""

from langchain.prompts.prompt import PromptTemplate

GRAPH_EXTRACTION_THINKING_TEMPLATE =\
"""Analyzing the provided text, please identify the entities present and outline their relationships with each other.
Please, show your work.

Text:
{input}
Answer: Let's think this out in a step by step way to be sure we have the right answer."""

GRAPH_EXTRACTION_TEMPLATE =\
"""
As an experienced Cypher expert, your goal is to analyze the provided text and generate a suitable Cypher CREATE query for populating a RedisGraph database.

Your Cypher query should prevent the creation of duplicate nodes in the database by using variables.
Use double quotes for nodes properties. Use only the name property of the nodes and avoid using any relationship properties.
Remove any trailing punctuation at the end of the query. Use only the relationship types for the predicate and avoid using nodes/labels for relations.

Ensure to follow the following format:
EXAMPLE
{example}
END OF EXAMPLE

Please provide the Cypher query as the output, without any additional information.

Text:
{input}
Thought:
{thought}
Output:"""

GRAPH_EXTRACTION_THINKING_PROMPT = PromptTemplate(
    input_variables=["input"],
    template=GRAPH_EXTRACTION_THINKING_TEMPLATE
)

GRAPH_EXTRACTION_PROMPT = PromptTemplate(
    input_variables=["input", "example", "thought"],
    template=GRAPH_EXTRACTION_TEMPLATE
)

GRAPH_EXAMPLE=\
"""
Output:
CREATE 
(e1:Task {name: "Blind Bake Pie Crust"}),
(e2:Task {name: "Cook Bacon"}),
... (N times depending on the number of entities)
(e13:Task {name: "Bake for 5 More Minutes"}),
(e6)-[:REQUIRES]->(e5),
... (N times depending on the number of relations)
(e12)-[:REQUIRES]->(e10),
(e13)-[:REQUIRES]->(e10)
"""