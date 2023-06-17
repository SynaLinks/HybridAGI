## The prompts for extracting graph as Cypher.
## Copyright (C) 2023 SynaLink.
##
## This program is free software: you can redistribute it and/or modify
## it under the tertext_editorms of the GNU General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with this program. If not, see <https://www.gnu.org/licenses/>.

from langchain.prompts.prompt import PromptTemplate

GRAPH_EXTRACTION_THINKING_TEMPLATE =\
"""Analyzing the provided text, please identify the entities present and outline their relationships with each other.

Text:
{input}
Answer: Let's think this out in a step by step way to be sure we have the right answer."""

GRAPH_EXTRACTION_TEMPLATE =\
"""
As an experienced Cypher expert, your goal is to analyze the provided text and generate a suitable Cypher CREATE query for populating a RedisGraph database.

Your Cypher query should prevent the creation of duplicate nodes in the database by using variables.
Use double quotes for nodes properties. Use only the name property of the nodes and avoid using any relationship properties.
Remove any trailing punctuation at the end of the query. Use only the relationship types for the predicate and avoid using nodes/labels for relations.

Please provide the Cypher query as the output, without any additional information.

Text:
{input}
Thoughts:
{thoughts}
Output:"""

GRAPH_EXTRACTION_THINKING_PROMPT = PromptTemplate(
    input_variables=["input"],
    template=GRAPH_EXTRACTION_THINKING_TEMPLATE
)

GRAPH_EXTRACTION_PROMPT = PromptTemplate(
    input_variables=["input", "thoughts"],
    template=GRAPH_EXTRACTION_TEMPLATE
)

