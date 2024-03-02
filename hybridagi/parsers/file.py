"""The file output parser. Copyright (C) 2023 SynaLinks. License: GPL-3.0"""

import re
from typing import Tuple, List
from langchain.schema import BaseOutputParser

PATTERN = \
r"(?P<filename>[a-zA-Z0-9_.-]+)\n```(?P<lang>[a-zA-Z]+)\n(?P<content>.*?)\n```"

class FileOutputParser(BaseOutputParser):
    """
    The Output Parser for the files
    """
    def parse(self, output:str) -> List[Tuple[str, str, str]]:
        """Fix and validate the given Cypher query."""
        filenames = []
        contents = []
        languages = []
        
        output = output.strip()
        matches = re.finditer(PATTERN, output, re.DOTALL)

        for match in matches:
            filenames.append(match.group('filename').replace("\_", "_"))
            contents.append(match.group('content').strip())
            languages.append(match.group('lang'))

        if len(filenames) == 0:
            instructions = self.get_format_instructions()
            raise ValueError(
                f"Invalid format. Could not parse the output. {instructions}"
            )
        return filenames, contents, languages

    def get_format_instructions(self) -> str:
        """Returns the formating instructions"""
        instructions = \
"""
The Input should follow the following format:
FILENAME
```LANG
CONTENT
```
Where the following tokens must be replaced such that:
FILENAME is the lowercase file name including the file extension.
LANG is the markup code block language for the content's language
and CONTENT its content.
"""
        return instructions