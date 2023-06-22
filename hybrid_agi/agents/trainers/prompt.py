"""The LLM based trainer. Copyright (C) 2023 SynaLinks. License: GPLv3"""

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