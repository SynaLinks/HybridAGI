from langchain.prompts.prompt import PromptTemplate

PROGRAM_DESCRIPTION_TEMPLATE = \
"""Please give me a short description of the following program:
```cypher
{program}
```
ProgramDescription:"""

PROGRAM_DESCRIPTION_PROMPT = PromptTemplate(
    input_variables = ["program"],
    template = PROGRAM_DESCRIPTION_TEMPLATE
)
