## The path output parser.
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

from langchain.schema import BaseOutputParser

class PathOutputParser(BaseOutputParser):
    """
    The Output Parser for the HybridAGI tools
    """
    def parse(self, output:str) -> str:
        """
        Fix and validate the given Cypher query.

        Args:
            output (str): The output of the LLM.
        """
        return self.fix_path(output)

    def get_format_instructions(self) -> str:
        """
        Returns the formating instructions

        Returns:
            str: The output format instructions 
        """
        instructions = "The output should be a unix-like path"
        return instructions

    def fix_path(self, path):
        path = path.replace('"', "")
        path = path.strip()
        if len(path) > 1:
            if path[len(path)-1] == "/":
                path = path[:len(path)-1]
        return path