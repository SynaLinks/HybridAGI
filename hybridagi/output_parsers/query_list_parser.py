from .output_parser import OutputParser
from hybridagi.core.datatypes import Query, QueryList

class QueryListOutputParser(OutputParser):
    """
    The output Parser for search queries
    """
    
    def parse(self, output:str) -> QueryList:
        """Fix the given query"""
        output_list = output.split(",")
        query_list = QueryList()
        if len(output_list) > 1:
            query_list.queries = [Query(query=o.replace("\"", "").strip()) for o  in output_list]
        else:
            query_list.queries = [Query(query=output.replace("\"", "").strip())]
        return query_list