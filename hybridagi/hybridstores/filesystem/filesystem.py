from ..hybridstore import HybridStore
from typing import List, Dict, Optional
from .path import dirname
# TODO replace langchain with llama-index or custom implementation
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document

from .context import FileSystemContext
from ...embeddings.base import BaseEmbeddings

class FileSystem(HybridStore):

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

    def add_texts(
            self,
            texts: List[str],
            ids: List[str] = [],
            descriptions: List[str] = [],
            metadatas: List[Dict[str, str]] = [],
        ) -> List[str]:
        """Method to add texts"""
        assert(len(texts) == len(ids))
        for idx, text in enumerate(texts):
            path = ids[idx]
            metadata = metadatas[idx] if metadatas else {}
            if self.exists(path):
                self.remove_documents([path])
            text_splitter = \
            RecursiveCharacterTextSplitter(
                chunk_size=self.chunk_size,
                chunk_overlap=self.chunk_overlap,
            )
            if isinstance(text, Document):
                sub_docs = text_splitter.split_documents(
                    [text]
                )
            elif isinstance(text, str):
                sub_docs = text_splitter.split_documents(
                    [Document(page_content=text, metadata=metadata)]
                )
            subdocs_texts = [d.page_content for d in sub_docs]
            subdocs_metadatas = [d.metadata for d in sub_docs]
            indexes = super().add_texts(
                texts = subdocs_texts,
                metadatas = subdocs_metadatas,
            )
            if len(indexes) > 0:
                self.create_document(path)
                for i, key in enumerate(indexes):
                    self.hybridstore.query(
                        'MATCH (n:Document {name:"'+path+'"}),'+
                        ' (m:Content {name:"'+key+'"}) MERGE (n)-[:CONTAINS]->(m)')
                    if i > 0:
                        self.hybridstore.query(
                            'MATCH (n:Content {name:"'+indexes[i-1]+'"}),'+
                            ' (m:Content {name:"'+key+'"}) MERGE (n)-[:NEXT]->(m)')
                self.hybridstore.query(
                    'MATCH (n:Document {name:"'+path+'"}),'+
                    ' (m:Content {name:"'+indexes[0]+'"}) MERGE (n)-[:BOF]->(m)')
                self.hybridstore.query(
                    'MATCH (n:Document {name:"'+path+'"}),'+
                    ' (m:Content {name:"'+indexes[-1]+'"}) MERGE (n)-[:EOF]->(m)')
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
            result = self.hybridstore.query(
                'MATCH (n:Content {name:"'+bof+'"}) RETURN n')
            content_key = result.result_set[0][0].properties["name"]
            content = self.get_content(content_key)
            text = content
        else:
            result = self.hybridstore.query(
                'MATCH path=(:Content {name:"'+bof+'"})'+
                '-[:NEXT*]->(:Content {name:"'+eof+'"}) RETURN nodes(path)')
            all_content = []
            for node in result.result_set[0][0]:
                content_key = node.properties["name"]
                content = self.get_content(content_key)
                all_content.append(content)
            text = "\n".join(all_content)
        return text

    def create_document(self, path:str):
        """Method to create a document (no check performed)"""
        self.hybridstore.query('MERGE (:Document {name: "'+path+'" })')
        parent_folder = dirname(path)
        while not parent_folder:
            self.hybridstore.query(
            'MATCH (n:Folder {name:"'+parent_folder+'"}),'+
            ' (m:Document {name:"'+path+'"}) MERGE (n)-[:CONTAINS]->(m)')
            parent_folder = dirname(path)
        self.hybridstore.query(
            'MATCH (n:Folder {name:"'+parent_folder+'"}),'+
            ' (m:Document {name:"'+path+'"}) MERGE (n)-[:CONTAINS]->(m)')

    def remove_documents(self, paths: List[str]):
        for path in paths:
            indexes = []
            result = self.hybridstore.query(
                'MATCH (c:Content)<-[:CONTAINS]-(d:Document {name:"'+
                path+'"}) RETURN c.name AS name')
            for record in result.result_set:
                indexes.append(record[0])
            self.hybridstore.query(
                'MATCH (c:Content)<-[:CONTAINS]-(d:Document {name:"'+
                path+'"}) DELETE c, d')

    def create_folder(self, path:str):
        """Method to create a folder (no check performed)"""
        self.hybridstore.query('MERGE (n:Folder {name:"'+path+'"})')
        parent_folder = dirname(path)
        self.hybridstore.query(
            'MATCH (n:Folder {name:"'+parent_folder+'"}),'+
            ' (m:Folder {name:"'+path+'"}) MERGE (n)-[:CONTAINS]->(m)')

    def is_folder(self, path:str) -> bool:
        """Method to check if a folder at path is present in the hybridstore"""
        result = self.hybridstore.query('MATCH (n:Folder {name:"'+path+'"}) RETURN n')
        if len(result.result_set) > 0:
            return True
        return False

    def is_empty(self, path:str) -> bool:
        """Method to check if a folder at path is empty in the hybridstore"""
        result = self.hybridstore.query(
            'MATCH (n:Folder {name:"'+path+'"})-[:CONTAINS]->(:Document) RETURN n')
        if len(result.result_set) == 0:
            return True
        return False

    def is_file(self, path:str) -> bool:
        """Method to check if a file at path is present in the hybridstore"""
        result = self.hybridstore.query('MATCH (n:Document {name:"'+path+'"}) RETURN n')
        if len(result.result_set) > 0:
            return True
        return False

    def is_beginning_of_file(self, content_index:str) -> bool:
        """Returns True if the content is the beginning of the file"""
        result = self.hybridstore.query(
            'MATCH (n:Content {name:"'+content_index+'"})<-[:BOF]-() RETURN n')
        if len(result.result_set) > 0:
            return True
        return False

    def is_end_of_file(self, content_index:str) -> bool:
        """Returns True if the content is the end of the file"""
        result = self.hybridstore.query(
            'MATCH (n:Content {name:"'+content_index+'"})<-[:EOF]-() RETURN n')
        if len(result.result_set) > 0:
            return True
        return False
    
    def get_beginning_of_file(self, path: str) -> str:
        """Method to return the BOF content index"""
        result = self.hybridstore.query(
            'MATCH (:Document {name:"'+path+'"})-[:BOF]->(n:Content) RETURN n')
        return result.result_set[0][0].properties["name"]

    def get_end_of_file(self, path: str) -> str:
        """Method to return the EOF content index"""
        result = self.hybridstore.query(
            'MATCH (:Document {name:"'+path+'"})-[:EOF]->(n:Content) RETURN n')
        return result.result_set[0][0].properties["name"]

    def get_next(self, content_index: str) -> str:
        """Method to return the next content index"""
        result = self.hybridstore.query(
            'MATCH (:Content {name:"'+content_index+'"})-[:NEXT]->(n:Content) RETURN n')
        if len(result) > 0:
            return result.result_set[0][0].properties["name"]
        return ""