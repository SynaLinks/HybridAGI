## The LLM based trainer.
## Copyright (C) 2023 SynaLinks.
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

TRAINER_TEMPLATE=\
"""
{self_description}
{core_values}
Your current assignment is to create a training program in {n} distinct tasks.
You are at a proficiency level comparable to a {level}.
Your objective is to become an expert in: {expertise}.

Before proceeding with the training, please consider the tasks already mastered.
The list of previously learned tasks is as follows:
LEARNED TASKS
{tasks}
END OF LEARNED TASKS

Be carefull to not learn the same things multiple times.
Your Output should be a list of practical exercices (like implementing code, writing a report etc.) be specific.

Ensure to use the following format:
EXAMPLE
- Writing a report about...
... (N times depending on the number of tasks)
- Implementing a function to ...
END OF EXAMPLE

Output:"""

TRAINER_PROMPT = PromptTemplate(
    input_variables = ["self_description", "core_values", "n", "level", "tasks", "expertise"],
    template = TRAINER_TEMPLATE
)

TRAINING_SUMMARIZER_TEMPLATE=\
"""
Please summarize the given tasks into other tasks.

Ensure to use the following format:
EXAMPLE
- First task performed
... (N times depending on the number of tasks)
- Last task performed
END OF EXAMPLE

Tasks:
{tasks}
Output:"""

TRAINING_SUMMARIZER_PROMPT = PromptTemplate(
    input_variables = ["tasks"],
    template = TRAINING_SUMMARIZER_TEMPLATE
)