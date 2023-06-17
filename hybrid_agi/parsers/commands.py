import shlex
from typing import List
from langchain.schema import BaseOutputParser

class CommandsOutputParser(BaseOutputParser):
    """The output parser for the VirtualShell"""
    def parse(self, output: str) -> List[List[str]]:
        """
        Parse the output.

        Args:
            output (str): The output of the LLM.
        """
        lexer = shlex.shlex(output, punctuation_chars=True)
        lexer.whitespace_split = True
        lexer.quotes = '"'
        tokens = list(lexer)
        # Extract the command arguments and logical operators
        arguments = []
        operators = []
        commands = []
        for token in tokens:
            if token in ['&&', '||', ';']:
                operators.append(token)
            else:
                arguments.append(token)

        # Separate the arguments into groups based on logical operators
        argument_groups = []
        current_group = []
        for arg, op in zip(arguments, operators):
            if op == ';':
                argument_groups.append(current_group)
                current_group = []
            else:
                current_group.append(arg)
        if current_group:
            argument_groups.append(current_group)

        return argument_groups

    def get_format_instructions(self) -> str:
        """
        Returns the formating instructions

        Returns:
            str: The output format instructions 
        """
        return "The Output should be a unix-like shell command"