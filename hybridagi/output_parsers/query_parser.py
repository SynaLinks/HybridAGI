from .output_parser import OutputParser
from hybridagi.core.datatypes import Query

class QueryOutputParser(OutputParser):
    """
    The output Parser for search queries
    """
    
    def parse(self, output:str) -> Query:
        """Fix the given query"""
        output = output.strip("\\")
        query = Query()
        query.query = output.replace("\"", "").strip()
        return query