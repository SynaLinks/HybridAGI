from .output_parser import OutputParser
from typing import Any

class CypherOutputParser(OutputParser):
    """
    The output parser for Cypher requests
    """

    def parse(self, output: str) -> Any:
        pattern = r"```cypher\n\n(.*?)\n```"
        matches = re.findall(pattern, markdown_text, re.DOTALL)
        output = matches[-1]
        output = output.rstrip("\";,.'")
        return output