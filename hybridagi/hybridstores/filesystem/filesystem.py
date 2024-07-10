"""The filesystem memory. Copyright (C) 2024 SynaLinks. License: GPL-3.0"""

import os
from ..hybridstore import HybridStore
from typing import List, Dict, Optional, Any
from .path import dirname, join

from ...text_splitters.sentence import SentenceTextSplitter

from .context import FileSystemContext
from ...embeddings.base import BaseEmbeddings

class FileSystem(HybridStore):
    """The filesystem memory"""

    def __init__(
        self,
        index_name: str,
        embeddings: BaseEmbeddings,
        context: Optional[FileSystemContext] = None,
        graph_index: str = "filesystem",
        hostname: str = "localhost",
        port: int = 6379,
        username: str = "",
        password: str = "",
        indexed_label: str = "Content",
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
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.init()

    def add_texts(
            self,
            texts: List[str],
            ids: List[str] = [],
            descriptions: List[str] = [],
            metadatas: List[Dict[Any, Any]] = [],
        ) -> List[str]:
        """Method to add texts"""
        indexes = []
        assert(len(texts) == len(ids))
        if metadatas:
            assert(len(texts) == len(metadatas))
        for idx, text in enumerate(texts):
            path = ids[idx]
            metadata = metadatas[idx] if metadatas else {}
            metadata["filename"] = path
            if self.exists(path):
                self.remove_documents([path])
            text_splitter = \
            SentenceTextSplitter(
                chunk_size=self.chunk_size,
                chunk_overlap=self.chunk_overlap,
            )
            subdocs_texts = text_splitter.split_text(text)
            if metadata:
                subdocs_metadatas = [metadata for _ in range(len(subdocs_texts))]
            else:
                subdocs_metadatas = []
            indexes = super().add_texts(
                texts = subdocs_texts,
                metadatas = subdocs_metadatas,
            )
            if len(indexes) > 0:
                self.create_document(path)
                for i, key in enumerate(indexes):
                    params = {"path": path, "index": key}
                    self.hybridstore.query(
                        'MATCH (n:Document {name:$path}),'+
                        ' (m:Content {name:$index}) MERGE (n)-[:CONTAINS]->(m)',
                        params = params,
                    )
                    if i > 0:
                        params = {"previous_index": indexes[i-1], "index": key}
                        self.hybridstore.query(
                            'MATCH (n:Content {name:$previous_index}),'+
                            ' (m:Content {name:$index}) MERGE (n)-[:NEXT]->(m)',
                            params = params,
                        )
                params = {"path": path, "index": indexes[0]}
                self.hybridstore.query(
                    'MATCH (n:Document {name:$path}),'+
                    ' (m:Content {name:$index}) MERGE (n)-[:BOF]->(m)',
                    params = params,
                )
                params = {"path": path, "last_index": indexes[0]}
                self.hybridstore.query(
                    'MATCH (n:Document {name:$path}),'+
                    ' (m:Content {name:$last_index}) MERGE (n)-[:EOF]->(m)',
                    params = params,
                )
        return indexes

    def append_texts(
            self,
            texts: List[str],
            ids: List[str] = [],
            descriptions: List[str] = [],
            metadatas: List[Dict[Any, Any]] = [],
        ) -> List[str]:
        """Method to append texts"""
        indexes = []
        assert(len(texts) == len(ids))
        for idx, text in enumerate(texts):
            path = ids[idx]
            metadata = metadatas[idx] if metadatas else {}
            if not self.exists(path):
                self.add_texts(
                    texts = [text],
                    ids = [path],
                    metadatas = [metadata],
                )
            else:
                text_splitter = \
                SentenceTextSplitter(
                    chunk_size=self.chunk_size,
                    chunk_overlap=self.chunk_overlap,
                )
                subdocs_texts = text_splitter.split_text(text)
                if metadata:
                    subdocs_metadatas = [metadata for _ in range(subdocs_texts)]
                else:
                    subdocs_metadatas = []
                indexes = super().add_texts(
                    texts = subdocs_texts,
                    metadatas = subdocs_metadatas,
                )
                eof = self.get_end_of_file(path)
                if len(indexes) > 0:
                    for i, index in enumerate(indexes):
                        params = {"path": path, "index": index}
                        self.hybridstore.query(
                            'MATCH (n:Document {name:$path}),'+
                            ' (m:Content {name:$index}) MERGE (n)-[:CONTAINS]->(m)',
                            params = params,
                        )
                        if i > 0:
                            params = {"previous_index": indexes[i-1], "index": index}
                            self.hybridstore.query(
                                'MATCH (n:Content {name:$previous_index}),'+
                                ' (m:Content {name:$index}) MERGE (n)-[:NEXT]->(m)',
                                params = params,
                            )
                    params = {"eof_index": eof, "first_index": indexes[0]}
                    self.hybridstore.query(
                        'MATCH (n:Content {name:$eof_index}),'+
                        ' (m:Content {name:$first_index}) MERGE (n)-[:NEXT]->(m)',
                        params = params,
                    )
                    params = {"path": path}
                    self.hybridstore.query(
                        'MATCH (n:Document {name:$path})-[r:EOF]->() DELETE r',
                        params = params,
                    )
                    params = {"path": path, "last_index": indexes[-1]}
                    self.hybridstore.query(
                        'MATCH (n:Document {name:$path}),'+
                        ' (m:Content {name:$last_index}) MERGE (n)-[:EOF]->(m)',
                        params = params,
                    )
        return indexes

    def get_document(self, path:str) -> str:
        """
        Method to get the full document.
        Do not use it for the LLM tools as it can exceed the max token.
        """
        if self.exists(path, label = "Document"):
            if self.is_folder(path):
                return "Cannot read directory."
        else:
            return "No such file or directory."
        text = ""
        bof = self.get_beginning_of_file(path)
        eof = self.get_end_of_file(path)
        if bof == eof:
            params = {"bof_index": bof}
            result = self.hybridstore.query(
                'MATCH (n:Content {name:$bof_index}) RETURN n',
                params = params,
            )
            content_key = result.result_set[0][0].properties["name"]
            content = self.get_content(content_key)
            text = content
        else:
            params = {"bof_index": bof, "eof_index": eof}
            result = self.hybridstore.query(
                'MATCH path=(:Content {name:$bof_index})'+
                '-[:NEXT*]->(:Content {name:$eof_index}) RETURN nodes(path)',
                params = params,
            )
            all_content = []
            for node in result.result_set[0][0]:
                content_key = node.properties["name"]
                content = self.get_content(content_key)
                all_content.append(content)
            text = "\n".join(all_content)
        return text

    def create_document(self, path:str):
        """Method to create a document (no check performed)"""
        params = {"path": path}
        self.hybridstore.query('MERGE (:Document {name:$path})', params = params)
        parent_folder = dirname(path)
        while not parent_folder:
            params = {"parent_folder": parent_folder, "path": path}
            self.hybridstore.query(
                'MATCH (n:Folder {name:$parent_folder}),'+
                ' (m:Document {name:$path}) MERGE (n)-[:CONTAINS]->(m)',
                params = params,
            )
            parent_folder = dirname(path)
        params = {"parent_folder": parent_folder, "path": path}
        self.hybridstore.query(
            'MATCH (n:Folder {name:$parent_folder}),'+
            ' (m:Document {name:$path}) MERGE (n)-[:CONTAINS]->(m)',
            params = params,
        )

    def remove_documents(self, paths: List[str]):
        for path in paths:
            indexes = []
            params = {"path": path}
            result = self.hybridstore.query(
                'MATCH (c:Content)<-[:CONTAINS]-(d:Document {name:$path}) RETURN c.name AS name',
                params = params,
            )
            for record in result.result_set:
                indexes.append(record[0])
            params = {"path": path}
            self.hybridstore.query(
                'MATCH (c:Content)<-[:CONTAINS]-(d:Document {name:$path}) DELETE c, d',
                params = params,
            )

    def create_folder(self, path:str):
        """Method to create a folder (no check performed)"""
        params = {"path": path}
        self.hybridstore.query('MERGE (n:Folder {name:$path})', params = params)
        parent_folder = dirname(path)
        params = {"parent_folder": parent_folder, "path": path}
        self.hybridstore.query(
            'MATCH (n:Folder {name:$parent_folder}),'+
            ' (m:Folder {name:$path}) MERGE (n)-[:CONTAINS]->(m)',
            params = params,
        )

    def is_folder(self, path:str) -> bool:
        """Method to check if a folder at path is present in the hybridstore"""
        params = {"path": path}
        result = self.hybridstore.query('MATCH (n:Folder {name:$path}) RETURN n',
            params = params,
        )
        if len(result.result_set) > 0:
            return True
        return False

    def is_empty(self, path:str) -> bool:
        """Method to check if a folder at path is empty in the hybridstore"""
        params = {"path": path}
        result = self.hybridstore.query(
            'MATCH (n:Folder {name:$path})-[:CONTAINS]->(:Document) RETURN n',
            params = params,
        )
        if len(result.result_set) == 0:
            return True
        return False

    def is_file(self, path:str) -> bool:
        """Method to check if a file at path is present in the hybridstore"""
        params = {"path": path}
        result = self.hybridstore.query('MATCH (n:Document {name:$path}) RETURN n',
            params = params,
        )
        if len(result.result_set) > 0:
            return True
        return False

    def is_beginning_of_file(self, content_index:str) -> bool:
        """Returns True if the content is the beginning of the file"""
        params = {"index": content_index}
        result = self.hybridstore.query(
            'MATCH (n:Content {name:$index})<-[:BOF]-() RETURN n',
            params = params,
        )
        if len(result.result_set) > 0:
            return True
        return False

    def is_end_of_file(self, content_index:str) -> bool:
        """Returns True if the content is the end of the file"""
        params = {"index": content_index}
        result = self.hybridstore.query(
            'MATCH (n:Content {name:$index})<-[:EOF]-() RETURN n')
        if len(result.result_set) > 0:
            return True
        return False
    
    def get_beginning_of_file(self, path: str) -> str:
        """Method to return the BOF content index"""
        params = {"path": path}
        result = self.hybridstore.query(
            'MATCH (:Document {name:$path})-[:BOF]->(n:Content) RETURN n',
            params = params,
        )
        return result.result_set[0][0].properties["name"]

    def get_end_of_file(self, path: str) -> str:
        """Method to return the EOF content index"""
        params = {"path": path}
        result = self.hybridstore.query(
            'MATCH (:Document {name:$path})-[:EOF]->(n:Content) RETURN n',
            params = params,
        )
        return result.result_set[0][0].properties["name"]

    def get_next(self, content_index: str) -> str:
        """Method to return the next content index"""
        params = {"index": content_index}
        result = self.hybridstore.query(
            'MATCH (:Content {name:$index})-[:NEXT]->(n:Content) RETURN n',
            params = params,
        )
        if len(result.result_set) > 0:
            return result.result_set[0][0].properties["name"]
        return ""

    def init(self):
        """Method to initialize the filesystem"""
        self.hybridstore.query('MERGE (:Folder {name:"/"})')
        self.create_folder("/home")
        self.create_folder("/home/user")
        self.create_folder("/home/user/Downloads")
        self.create_folder("/home/user/Documents")
        self.create_folder("/home/user/Pictures")
        self.create_folder("/home/user/Music")

    def clear(self):
        super().clear()
        self.init()