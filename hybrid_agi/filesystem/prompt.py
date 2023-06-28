"""The prompt for updating text. Copyright (C) 2023 SynaLinks. License: GPL-3.0"""

UPDATE_TEXT_TEMPLATE=\
"""
Please Output update the input Text to integrate the following Modifications if relevant.
If no Modifications are relevant, Output the unchanged Text.

Text:
{text}
Modifications:
{modifications}
Output:"""

UPDATE_TEXT_PROMPT = PromptTemplate(
    input_variables = ["text", "modifications"],
    template = UPDATE_TEXT_TEMPLATE
)