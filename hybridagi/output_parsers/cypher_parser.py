import abc
from typing import Any

class CypherParser():
    """
    The output parser for Cypher requests
    """

    def parse(self, output: str) -> Any:
        pattern = r"```cypher\n\n(.*?)\n```"
        matches = re.findall(pattern, markdown_text, re.DOTALL)
        output = matches[-1]
        output = output.rstrip("\";,.'")
        return output