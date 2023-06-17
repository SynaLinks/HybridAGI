## The prompts for extracting summary.
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