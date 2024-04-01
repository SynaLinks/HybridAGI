import uuid
import os
from falkordb import Node, Graph
from typing import List, Dict, Optional, Tuple
from ..hybridstore import HybridStore
from ...embeddings.base import BaseEmbeddings

RESERVED_NAMES = [
    "main",
    "playground",
    "filesystem",
    "program_memory",
    "trace_memory",
    "\u006D\u0061\u0069\u006E",
    "\u0070\u006C\u0061\u0079\u0067\u0072\u006F\u0075\u006E\u0064",
    "\u0066\u0069\u006C\u0065\u0073\u0079\u0073\u0074\u0065\u006D",
    "\u0070\u0072\u006F\u0067\u0072\u0061\u006D\u005F\u006D\u0065\u006D\u006F\u0072\u0079",
    "\u0074\u0072\u0061\u0063\u0065\u005F\u006D\u0065\u006D\u006F\u0072\u0079",
]

class ProgramMemory(HybridStore):

    def __init__(
            self,
            index_name: str,
            embeddings: BaseEmbeddings,
            graph_index: str = "program_memory",
            hostname: int = "localhost",
            port: int = 6379,
            username: str = "",
            password: str = "",
            indexed_label: str = "Content",
            wipe_on_start: bool = False,
            ):
        super().__init__(
            index_name = index_name,
            graph_index = graph_index,
            embeddings = embeddings,
            hostname = hostname,
            port = port,
            username = username,
            password = password,
            indexed_label = indexed_label,
            wipe_on_start = wipe_on_start,
        )

    def from_folders(
            self,
            folders: List[str],
        ):
        """Method to load a library of programs, no check performed"""
        names = []
        programs = []
        for programs_folder in folders:
            for dirpath, dirnames, filenames in os.walk(programs_folder):
                for filename in filenames:
                    if filename.endswith(".cypher"):
                        program_name = filename.replace(".cypher", "")
                        try:
                            names.append(program_name)
                            source = os.path.join(dirpath, filename)
                            programs.append(open(source, "r").read())
                        except Exception:
                            pass
        self.add_texts(texts = programs, ids = names)

    def add_texts(
            self,
            texts: List[str],
            ids: List[str] = [],
            descriptions: List[str] = [],
            metadatas: List[Dict[str, str]] = [],
        ):
        """Method to add programs"""
        indexes = []
        dependencies = {}
        for idx, text in enumerate(texts):
            content_index = str(uuid.uuid4().hex) if not ids else ids[idx]
            if descriptions:
                description = descriptions[idx]
            else:
                description = ""
                for line in text.split("\n"):
                    if line.startswith("// @desc:"):
                        description = line.replace("// @desc:", "").strip()
                        break
                    elif line.startswith("//"):
                        pass
                    elif not line:
                        pass
                    else:
                        break
            graph_program = self.get_graph(content_index)
            try:
                graph_program.delete()
            except Exception:
                pass
            try:
                graph_program.query(text)
            except Exception as e:
                raise RuntimeError(f"{content_index}: {e}")
            params = {"index": content_index}
            self.hybridstore.query(
                'MERGE (n:Program {name:$index})',
                params = params,
            )
            metadata = {} if not metadatas else metadatas[idx]
            if description:
                vector = self.embeddings.embed_text(description)
            else:
                vector = self.embeddings.embed_text(text)
            params = {"index": content_index, "vector": vector.tolist()}
            self.hybridstore.query(
               'MERGE (n:'+self.indexed_label+' {name:$index, embeddings_vector:vecf32($vector)})',
               params = params,
            )
            self.set_content(content_index, text)
            if description:
                self.set_content_description(content_index, description)
            if metadata:
                self.set_content_metadata(content_index, metadata)
            params = {"index": content_index}
            self.hybridstore.query(
                "MATCH (p:Program {name:$index}), (c:Content {name:$index}) MERGE (p)-[:CONTAINS]->(c)",
                params = params,
            )
            indexes.append(content_index)
            result = graph_program.query(
                'MATCH (n:Program) RETURN n.program AS program'
            )
            if len(result.result_set) > 0:
                dependencies[content_index] = []
                for record in result.result_set:
                    dependencies[content_index].append(record[0])
        for index, dependency_list in dependencies.items():
            for dependency in dependency_list:
                params = {"index": index, "dependency": dependency}
                self.hybridstore.query(
                    "MATCH (p:Program {name:$index}), (d:Program {name:$dependency}) MERGE (p)-[:DEPENDS_ON]->(d)",
                    params = params,
                )
        return indexes

    def depends_on(self, source: str, target: str):
        """Method to check if a program depend on another"""
        params = {"source": source, "target": target}
        result = self.hybridstore.query(
            "MATCH (n:Program {name:$source})-[r:DEPENDS_ON*]->(m:Program {name:$target}) RETURN r",
            params = params,
        )
        if len(result.result_set) > 0:
            return True
        return False

    def get_program_names(self):
        """Method to get the program names"""
        program_names = []
        result = self.hybridstore.query("MATCH (n:Program) RETURN n.name AS name")
        for record in result:
            program_names.append(record[0])
        return program_names

    def is_protected(self, program_name: str):
        if program_name in RESERVED_NAMES:
            return True
        else:
            if self.depends_on("main", program_name):
                return True
        return False

    def get_next_node(self, node: Node, program: Graph) -> Optional[Node]:
        """Method to get the next node"""
        try:
            name = node.properties["name"]
        except ValueError:
            raise ValueError("Invalid node: missing required 'name' parameter")
        params = {"name": name}
        result = program.query(
            'MATCH ({name:$name})-[:NEXT]->(m) RETURN m',
            params=params,
        )
        if len(result.result_set) > 0:
            return result.result_set[0][0]
        return None

    def get_starting_node(self, program_name: str) -> Node:
        """Method to get the starting node of the given program"""
        program = self.get_graph(program_name)
        result = program.query(
            'MATCH (n:Control {name:"Start"}) RETURN n')
        if len(result.result_set) == 0:
            raise RuntimeError("No entry point detected,"+
                " please make sure you loaded the programs.")
        if len(result.result_set) > 1:
            raise RuntimeError("Multiple entry point detected,"+
                " please correct your programs.")
        starting_node = result.result_set[0][0]
        return starting_node