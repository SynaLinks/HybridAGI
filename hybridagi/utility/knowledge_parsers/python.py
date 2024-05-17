import tree_sitter_python as tspython
from tree_sitter import Language, Parser, Tree, Node
from .base import KnowledgeParserBase
from ...hybridstores.fact_memory.fact_memory import FactMemory

PY_LANGUAGE = Language(tspython.language())

class PythonKnowledgeParser(KnowledgeParserBase):

    def __init__(
            self,
            fact_memory: FactMemory,
        ):
        super().__init__(fact_memory = fact_memory)
        self.parser = Parser(PY_LANGUAGE)

    def parse(self, filename:str, code: str):
        src = code.encode('utf-8')
        tree = self.parser.parse(src)
        # Get class names and body
        query = PY_LANGUAGE.query("""
(class_definition
    name: (identifier) @class-name
    body: (block) @class-body)
"""
            )
        matches = query.matches(tree.root_node)
        for record in matches:
            class_name = src[record[1]["class-name"].start_byte:record[1]["class-name"].end_byte]
            class_body = src[record[1]["class-body"].start_byte:record[1]["class-body"].end_byte]
            class_name = class_name.decode('utf8')
            class_body = class_body.decode('utf8')
            metadata = {}
            metadata["filename"] = filename
            self.fact_memory.add_texts(
                texts = [class_body],
                ids = [class_name],
                descriptions = [class_name],
                metadatas = [metadata],
            )
        query = PY_LANGUAGE.query("""
(class_definition
    name: (identifier) @class-name
    superclasses: (argument_list
        (identifier) @super-class))
"""
        )
        matches = query.matches(tree.root_node)
        for record in matches:
            class_name = src[record[1]["class-name"].start_byte:record[1]["class-name"].end_byte]
            super_class = src[record[1]["super-class"].start_byte:record[1]["super-class"].end_byte]
            class_name = class_name.decode('utf8')
            super_class = super_class.decode('utf8')
            self.fact_memory.add_triplet(class_name, "inherits from", super_class)
        query = PY_LANGUAGE.query("""
(class_definition
name: (identifier) @class-name
body: (block
    (function_definition
    name: (identifier) @method-name
    body: (block) @method-body)))
"""
        )
        matches = query.matches(tree.root_node)
        node_class = ""
        method_name = ""
        for record in matches:
            class_name = src[record[1]["class-name"].start_byte:record[1]["class-name"].end_byte]
            method_name = src[record[1]["method-name"].start_byte:record[1]["method-name"].end_byte]
            method_body = src[record[1]["method-body"].start_byte:record[1]["method-body"].end_byte]
            class_name = class_name.decode('utf8')
            method_name = method_name.decode('utf8')
            method_body = method_body.decode('utf8')
            metadata = {}
            metadata["filename"] = filename
            self.fact_memory.add_texts(
                texts = [method_body],
                ids = [class_name+":"+method_name],
                descriptions = [class_name+":"+method_name],
                metadatas = [metadata],
            )
            self.fact_memory.add_triplet(class_name, "has method", class_name+":"+method_name)