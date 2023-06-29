"""The Cypher output parser. Copyright (C) 2023 SynaLinks. License: GPL-3.0"""

from langchain.schema import BaseOutputParser

class CypherOutputParser(BaseOutputParser):
    """
    The Output Parser for RedisGraph Cypher query
    """

    def parse(self, output:str) -> str:
        """
        Fix and validate the given Cypher query.

        Args:
            output (str): The output of the LLM.
        """
        self.validate(output)
        return self.fix(output)

    def fix(self, output: str) -> str:
        """
        Fix RedisGraph Cypher query.

        Args:
            output (str): The Cypher query to be fixed.

        Returns:
            The corrected Cypher query for RedisGraph Python.

        Raises:
            ValueError: If the input query is not a string.
            ValueError: If the input query is empty.
        """
        # Remove any leading whitespace or newline characters
        output = output.lstrip()
        output = output.rstrip()
        output = output.strip()
        #Remove any trailing punctuation marks or quotes
        while output and output[-1] in [",", ".", ";", '"', "`", "'"]:
            output = output[:-1]
        return output

    def validate(self, output:str) -> str:
        """
        Validate the given Cypher query.

        Args:
            output (str): The Cypher query to validate.
        """
        if not isinstance(output, str):
            raise ValueError("The Cypher query must be a string")
        if not output:
            raise ValueError("The Cypher query cannot be empty")

    def get_format_instructions(self) -> str:
        """
        Returns the formating instructions

        Returns:
            str: The output format instructions 
        """
        instructions = "The output should follow RedisGraph Cypher query formalism. Ensure the output can be parsed using RedisGraph Python client."
        return instructions
