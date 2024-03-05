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
        """Fix and validate the output."""
        filenames = []
        contents = []
        languages = []
        
        output = output.strip()
        matches = re.finditer(PATTERN, output, re.DOTALL)

        for match in matches:
            filename = match.group('filename').replace("\_", "_")
            filename = filename.strip(".'\"")
            filenames.append(filename)
            contents.append(match.group('content').strip())
            languages.append(match.group('lang'))

        if len(filenames) == 0:
            raise ValueError(
                "Error while parsing the Input: Invalid format."\
                +" Please make sure that the file has a name and the format is correct."
            )
        return filenames, contents, languages