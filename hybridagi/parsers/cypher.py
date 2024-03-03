"""The Cypher output parser. Copyright (C) 2023 SynaLinks. License: GPL-3.0"""

from langchain.schema import BaseOutputParser

class CypherOutputParser(BaseOutputParser):
    """
    The Output Parser for RedisGraph Cypher queries
    """

    def parse(self, output:str) -> str:
        """Fix and validate the given Cypher query."""
        if not isinstance(output, str):
            raise ValueError("The Cypher query must be a string")
        if not output:
            raise ValueError("The Cypher query cannot be empty")
        return self.fix(output)

    def fix(self, output: str) -> str:
        """Fix RedisGraph Cypher query."""
        # Remove any leading whitespace or newline characters or trailing punctuaction
        output = output.strip()
        output = output.strip("\"'`")
        output = output.rstrip(".,;")
        return output

    def get_format_instructions(self) -> str:
        """Returns the formating instructions."""
        instructions = (
            "The output should follow RedisGraph Cypher query formalism."+
            " Ensure the output can be parsed using RedisGraph Python client."
        )
        return instructions
