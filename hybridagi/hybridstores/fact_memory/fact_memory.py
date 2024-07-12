"""The fact memory. Copyright (C) 2024 SynaLinks. License: GPL-3.0"""
# modifed from llama-index to add vector embeddings
# The MIT License

# Copyright (c) Jerry Liu

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import time
from ..hybridstore import HybridStore
from typing import List, Dict, Optional, Any
from ...embeddings.base import BaseEmbeddings

class FactMemory(HybridStore):
    """The fact memory"""

    def __init__(
        self,
        index_name: str,
        embeddings: BaseEmbeddings,
        graph_index: str = "fact_memory",
        hostname: str = "localhost",
        port: int = 6379,
        username: str = "",
        password: str = "",
        indexed_label: str = "Entity",
        wipe_on_start: bool = False,
        chunk_size: int = 1024,
        chunk_overlap: int = 0,
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
        self.schema = ""

    def get_rel_map(
        self, subjs: Optional[List[str]] = None, depth: int = 2, limit: int = 30
    ) -> Dict[str, List[List[str]]]:
        """Get flat rel map."""
        # The flat means for multi-hop relation path, we could get
        # knowledge like: subj -> rel -> obj -> rel -> obj -> rel -> obj.
        # This type of knowledge is useful for some tasks.
        # +-------------+------------------------------------+
        # | subj        | flattened_rels                     |
        # +-------------+------------------------------------+
        # | "player101" | [95, "player125", 2002, "team204"] |
        # | "player100" | [1997, "team204"]                  |
        # ...
        # +-------------+------------------------------------+

        rel_map: Dict[Any, List[Any]] = {}
        if subjs is None or len(subjs) == 0:
            # unlike simple graph_store, we don't do get_all here
            return rel_map

        query = f"""
            MATCH (n1:{self.indexed_label})
            WHERE n1.name IN $subjs
            WITH n1
            MATCH p=(n1)-[e*1..{depth}]->(z)
            RETURN p
            ORDER BY max([r IN relationships(p) | r.timestamp]) DESC
            LIMIT {limit}
        """

        data = self.hybridstore.query(query, params={"subjs": subjs})
        if not data.result_set:
            return rel_map

        for record in data.result_set:
            nodes = record[0].nodes()
            edges = record[0].edges()

            subj_id = nodes[0].properties["name"]
            path = []
            for i, edge in enumerate(edges):
                dest = nodes[i + 1]
                dest_id = dest.properties["name"]
                path.append(edge.relation)
                path.append(dest_id)

            paths = rel_map[subj_id] if subj_id in rel_map else []
            paths.append(path)
            rel_map[subj_id] = paths

        return rel_map

    def refresh_schema(self) -> None:
        """Refreshes the graph schema information."""
        node_properties = self.hybridstore.query("CALL db.PROPERTYKEYS()")
        relationships = self.hybridstore.query("CALL db.RELATIONSHIPTYPES()")

        self.schema = f"""
Properties: {node_properties.result_set}
Relationships: {relationships.result_set}
"""

    def get_schema(self, refresh: bool = True) -> str:
        """Get the schema of the hybridstore."""
        if self.schema and not refresh:
            return self.schema
        self.refresh_schema()
        return self.schema

    def get_triplets(self, subj: str) -> List[List[str]]:
        """Get triplets."""
        get_query = f"""
            MATCH (n1:`{self.indexed_label}`)-[r]->(n2:`{self.indexed_label}`)
            WHERE n1.id = $subj RETURN type(r), n2.id
        """
        result = self.hybridstore.query(
            get_query, params={"subj": subj}
        )
        return result.result_set

    def add_triplet(self, subj: str, rel: str, obj: str) -> None:
        """Add triplet."""

        query = """
            MERGE (n1:`%s` {name:$subj})
            MERGE (n2:`%s` {name:$obj})
            MERGE (n1)-[r:`%s`]->(n2)
            ON CREATE SET r.timestamp = $timestamp
        """

        prepared_statement = query % (
            self.indexed_label,
            self.indexed_label,
            rel.replace(" ", "_").upper(),
        )

        # Call with prepared statement
        self.hybridstore.query(prepared_statement, params={"subj": subj, "obj": obj, "timestamp": int(time.time())})

    def delete_triplet(self, subj: str, rel: str, obj: str) -> None:
        """Delete triplet."""

        def delete_rel(subj: str, obj: str, rel: str) -> None:
            rel = rel.replace(" ", "_").upper()
            query = f"""
                MATCH (n1:`{self.indexed_label}`)-[r:`{rel}`]->(n2:`{self.indexed_label}`)
                WHERE n1.name = $subj AND n2.name = $obj DELETE r
            """
            self.hybridstore.query(query, params={"subj": subj, "obj": obj})

        def delete_entity(entity: str) -> None:
            query = f"MATCH (n:`{self.indexed_label}`) WHERE n.name = $entity DELETE n"
            self.hybridstore.query(query, params={"entity": entity})

        def check_edges(entity: str) -> bool:
            query = f"""
                MATCH (n1:`{self.indexed_label}`)--()
                WHERE n1.name = $entity RETURN count(*)
            """
            result = self.hybridstore.query(
                query, params={"entity": entity}
            )
            return bool(result.result_set)

        delete_rel(subj, obj, rel)
        if not check_edges(subj):
            delete_entity(subj)
        if not check_edges(obj):
            delete_entity(obj)