"""The prompts for extracting summary. Copyright (C) 2023 SynaLinks. License: GPL-3.0"""

from langchain.prompts.prompt import PromptTemplate

SUMMARY_EXTRACTION_TEMPLATE =\
"""Analyzing the provided text, please summarize it.
If it is a code snippet, please explain it instead.

Text:
{input}
Answer: Let's think this out in a step by step way to be sure we have the right answer."""

SUMMARY_EXTRACTION_PROMPT = PromptTemplate(
    input_variables = ["input"],
    template = SUMMARY_EXTRACTION_TEMPLATE
)