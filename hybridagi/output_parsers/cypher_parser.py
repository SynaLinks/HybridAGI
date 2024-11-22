from .output_parser import OutputParser
import re
from typing import Any

class CypherOutputParser(OutputParser):
    """
    The output parser for Cypher requests
    """

    def parse(self, output: str) -> Any:
        output = output.replace(":Question", ":Decision")
        output = output.replace("CREATE //", "CREATE\n//")
        output = output.replace("CREATE (", "CREATE\n(")
        output = output.replace("});", "}),")
        output = output.replace("\" })", "\"})")
        output = output.replace("// Nodes declaration (", "// Nodes declaration\n(")
        output = output.replace("}) ", "}), ")
        output = output.replace("// Nodes declaration ", "// Nodes declaration\n")
        output = output.replace("// Structure declaration ", "// Structure declaration\n")
        output = output.replace("}), (", "}),\n(")
        output = output.replace("}), // Structure declaration", "}),\n// Structure declaration")
        output = output.replace("), (", "),\n(")
        output = "\n".join(output.split("\n"))
        pattern = r"```cypher\n(.*?)```"
        matches = re.findall(pattern, output, re.DOTALL)
        if len(matches) > 0:
            output = matches[-1]
        output = output.rstrip("\";,.'")
        return output