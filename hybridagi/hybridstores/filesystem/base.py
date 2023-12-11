from typing import Optional, Callable, Any
from .path import dirname
from ..hybridstore import BaseHybridStore
from langchain.schema.embeddings import Embeddings
from ..hybridstore import _default_norm

class BaseFileSystem(BaseHybridStore):
    """Base class for filesystem hybridstore"""

    def __init__(
            self,
            redis_url: str,
            index_name: str,
            embeddings: Embeddings,
            embeddings_dim: int,
            normalize: Optional[Callable[[Any], Any]] = _default_norm,
            verbose: bool = True):
        """Base filesystem constructor"""
        super().__init__(
            redis_url = redis_url,
            index_name = index_name,
            embeddings = embeddings,
            embeddings_dim = embeddings_dim,
            graph_index = "filesystem",
            indexed_label = "Content",
            normalize = normalize,
            verbose = verbose)

    def create_document(self, path:str):
        """Method to create a document (no check performed)"""
        self.query('MERGE (:Document {name: "'+path+'" })')
        parent_folder = dirname(path)
        self.query(
            'MATCH (n:Folder {name:"'+parent_folder+'"}),'+
            ' (m:Document {name:"'+path+'"}) MERGE (n)-[:CONTAINS]->(m)')

    def create_folder(self, path:str):
        """Method to create a folder (no check performed)"""
        self.query('MERGE (n:Folder {name:"'+path+'"})')
        parent_folder = dirname(path)
        self.query(
            'MATCH (n:Folder {name:"'+parent_folder+'"}),'+
            ' (m:Folder {name:"'+path+'"}) MERGE (n)-[:CONTAINS]->(m)')
    
    def exists(self, path:str) -> bool:
        """Method to check if an entry at path is present in the hybridstore"""
        result = self.query('MATCH (n {name:"'+path+'"}) RETURN n')
        if len(result) > 0:
            return True
        return False

    def is_folder(self, path:str) -> bool:
        """Method to check if a folder at path is present in the hybridstore"""
        result = self.query('MATCH (n:Folder {name:"'+path+'"}) RETURN n')
        if len(result) > 0:
            return True
        return False

    def is_empty(self, path:str) -> bool:
        """Method to check if a folder at path is empty in the hybridstore"""
        result = self.query(
            'MATCH (n:Folder {name:"'+path+'"})-[:CONTAINS]->(:Document) RETURN n')
        if len(result) == 0:
            return True
        return False

    def is_file(self, path:str) -> bool:
        """Method to check if a file at path is present in the hybridstore"""
        result = self.query('MATCH (n:Document {name:"'+path+'"}) RETURN n')
        if len(result) > 0:
            return True
        return False

    def is_beginning_of_file(self, content_index:str) -> bool:
        """Returns True if the content is the beginning of the file"""
        result = self.query(
            'MATCH (n:Content {name:"'+content_index+'"})<-[:BOF]-() RETURN n')
        if len(result) > 0:
            return True
        return False

    def is_end_of_file(self, content_index:str) -> bool:
        """Returns True if the content is the end of the file"""
        result = self.query(
            'MATCH (n:Content {name:"'+content_index+'"})<-[:EOF]-() RETURN n')
        if len(result) > 0:
            return True
        return False
    
    def get_beginning_of_file(self, path: str) -> str:
        """Method to return the BOF content index"""
        result = self.query(
            'MATCH (:Document {name:"'+path+'"})-[:BOF]->(n:Content) RETURN n')
        return result[0][0].properties["name"]

    def get_end_of_file(self, path: str) -> str:
        """Method to return the EOF content index"""
        result = self.query(
            'MATCH (:Document {name:"'+path+'"})-[:EOF]->(n:Content) RETURN n')
        return result[0][0].properties["name"]

    def get_next(self, content_index: str) -> str:
        """Method to return the next content index"""
        result = self.query(
            'MATCH (:Content {name:"'+content_index+'"})-[:NEXT]->(n:Content) RETURN n')
        if len(result) > 0:
            return result[0][0].properties["name"]
        return ""
    
    def initialize(self):
        """Method to initialize the filesystem"""
        super().initialize()
        self.query('MERGE (:Folder {name:"/"})')
        self.create_folder("/home")
        self.create_folder("/home/user")
        self.create_folder("/home/user/Downloads")
        self.create_folder("/home/user/Documents")
        self.create_folder("/home/user/Pictures")
        self.create_folder("/home/user/Music")