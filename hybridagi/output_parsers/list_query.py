"""The list query output parser. Copyright (C) 2023 SynaLinks. License: GPL-3.0"""

from .base import BaseOutputParser
from typing import List, Union

class ListQueryOutputParser(BaseOutputParser):
    """
    The Output Parser for search queries
    """
    def parse(self, output:str) -> Union[str, List[str]]:
        """Fix the given query"""
        output_list = output.split(" or ")
        if len(output_list) > 1:
            return [o.replace("\"", "").strip() for o  in output_list]
        else:
            return output.replace("\"", "").strip()