## The prompts for extracting plan as Cypher.
## Copyright (C) 2023 SynaLink.
##
## This program is free software: you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
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

PLAN_EXTRACTION_THINKING_TEMPLATE=\
"""Analyzing the provided text, please identify a set of tasks with its purposes and outline their requirements with each other.
Text:
{input}
Answer: Let's think this out in a step by step way to be sure we have the right answer."""

PLAN_EXTRACTION_TEMPLATE=\
"""As an experienced Cypher expert, your goal is to analyze the provided text and generate a suitable Cypher CREATE query for populating a RedisGraph database.
The RedisGraph structure extracted represents a hierarchical task network composed of a set of tasks.

Ensure to follow the following format:
EXAMPLE
{example}
END OF EXAMPLE

Take into account the chronological order of the tasks in the requirements.
Only use the label Task and the relation REQUIRES.

Please provide the RedisGraph Cypher query as the output, without any additional information.

Input:
{input}
Thought:
{thoughts}
Output:"""

PLAN_EXTRACTION_THINKING_PROMPT = PromptTemplate(
    input_variables=["input"],
    template=PLAN_EXTRACTION_THINKING_TEMPLATE
)

PLAN_EXTRACTION_PROMPT = PromptTemplate(
    input_variables=["input", "example", "thoughts"],
    template=PLAN_EXTRACTION_TEMPLATE
)

PLAN_EXAMPLE=\
"""
Text:
make a quiche lorraine
Output:
CREATE 
(t1:Task {name: "Blind Bake Pie Crust"}),
(t2:Task {name: "Cook Bacon"}),
(t3:Task {name: "Whisk Eggs and Cream"}),
(t4:Task {name: "Grate Cheese"}),
(t5:Task {name: "Assemble Quiche"}),
(t6:Task {name: "Add Bacon and Cheese"}),
(t7:Task {name: "Pour Egg Mixture"}),
(t8:Task {name: "Line Pie Crust with Parchment Paper"}),
(t9:Task {name: "Fill with Pie Weights"}),
(t10:Task {name: "Bake in Preheated Oven"}),
(t11:Task {name: "Bake for 10 Minutes"}),
(t12:Task {name: "Remove Pie Weights and Parchment Paper"}),
(t13:Task {name: "Bake for 5 More Minutes"}),
(t6)-[:REQUIRES]->(t5),
(t7)-[:REQUIRES]->(t5),
(t8)-[:REQUIRES]->(t1),
(t9)-[:REQUIRES]->(t1),
(t10)-[:REQUIRES]->(t1),
(t11)-[:REQUIRES]->(t10),
(t12)-[:REQUIRES]->(t10),
(t13)-[:REQUIRES]->(t10)
"""

PLAN_EXAMPLE_SMALL=\
"""
Text:
make a quiche lorraine
Output:
CREATE 
(t1:Task {name: "Blind Bake Pie Crust", purpose:"Prepare for filling"}),
(t2:Task {name: "Cook Bacon", purpose:"Add savor"}),
... (N times depending on the number of tasks)
(t13:Task {name: "Bake for 5 More Minutes", purpose:"Be sure to cook well"}),
(t6)-[:REQUIRES]->(t5),
... (N times depending on the number of requirements)
(t12)-[:REQUIRES]->(t10),
(t13)-[:REQUIRES]->(t10)
"""