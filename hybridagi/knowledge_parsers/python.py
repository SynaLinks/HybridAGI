from typing import Optional
import tree_sitter_python as tspython
from tree_sitter import Language, Parser, Tree, Node
from .base import BaseKnowledgeParser
from ..hybridstores.fact_memory.fact_memory import FactMemory
from ..hybridstores.filesystem.filesystem import FileSystem

PY_LANGUAGE = Language(tspython.language())

class PythonKnowledgeParser(BaseKnowledgeParser):

    def __init__(
            self,
            filesystem: FileSystem,
            fact_memory: FactMemory,
        ):
        super().__init__(
            filesystem = filesystem,
            fact_memory = fact_memory,
            valid_extensions = [".py"],
        )
        self.parser = Parser(PY_LANGUAGE)
        if filesystem is None:
            raise ValueError("")

    def parse(self, dest_path:str, content: str):
        self.filesystem.add_texts(
            texts=[content],
            ids=[dest_path],
        )
        src = content.encode('utf-8')
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
            metadata["filepath"] = dest_path
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
            metadata["filepath"] = filepath
            self.fact_memory.add_texts(
                texts = [method_body],
                ids = [class_name+":"+method_name],
                descriptions = [class_name+":"+method_name],
                metadatas = [metadata],
            )
            self.fact_memory.add_triplet(class_name, "has method", class_name+":"+method_name)

    def read(self, source_path: str) -> str:
        f = open(source_path, "r")
        file_content = f.read()
        return file_content