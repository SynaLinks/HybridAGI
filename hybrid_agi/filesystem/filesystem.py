"""The virtual filesystem. Copyright (C) 2023 SynaLinks. License: GPL-3.0"""

import os
import datetime
from colorama import Fore, Style
from pydantic import BaseModel, Extra
from typing import Optional, List, Dict, Callable
from langchain.schema import Document
from langchain.base_language import BaseLanguageModel
from hybrid_agi.hybridstores.redisgraph import RedisGraphHybridStore

def join(paths: List[str]) -> str:
        return '/'.join(paths)

def dirname(path:str) -> str:
    if path == "/":
        return path
    else:
        tokens = path.split('/')
        dirname = '/'.join(tokens[:-1])
        if dirname == "":
            return "/"
        return dirname

def basename(path:str) -> str:
    tokens = path.split('/')
    return tokens[-1]    

class FileSystemContext(BaseModel):
    """The filesystem context."""
    home_directory:str = "/home/user"
    working_directory:str = "/home/user"
    previous_working_directory:str = "/home/user"

    def eval_path(self, path:str):
        """Method to eval unix-like path"""
        if path != "":
            if path.startswith(".."):
                path = dirname(self.working_directory) + path[2:]
            elif path.startswith("."):
                path = self.working_directory + path[1:]
            elif path.startswith("~"):
                path = self.home_directory + path[1:]
            elif path == "-":
                path = self.previous_working_directory
            if not path.startswith("/"):
                path = join([self.working_directory, path])
        else:
            path = self.working_directory
        return path

class FileSystemUtility(BaseModel):
    hybridstore: RedisGraphHybridStore

    class Config:
        """Configuration for this pydantic object."""
        extra = Extra.forbid
        arbitrary_types_allowed = True

    def exists(self, path:str) -> bool:
        """Method to check if an entry at path is present in the hybridstore"""
        result = self.hybridstore.metagraph.query('MATCH (n {name:"'+path+'"}) RETURN n')
        if len(result.result_set) > 0:
            return True
        return False

    def is_folder(self, path:str) -> bool:
        """Method to check if a folder at path is present in the hybridstore"""
        result = self.hybridstore.metagraph.query('MATCH (n:Folder {name:"'+path+'"}) RETURN n')
        if len(result.result_set) > 0:
            return True
        return False

    def is_empty(self, path:str) -> bool:
        """Method to check if a folder at path is empty in the hybridstore"""
        result = self.hybridstore.metagraph.query('MATCH (n:Folder {name:"'+path+'"})-[:CONTAINS]->(:Document) RETURN n')
        if len(result.result_set) == 0:
            return True
        return False

    def is_file(self, path:str) -> bool:
        """Method to check if a file at path is present in the hybridstore"""
        result = self.hybridstore.metagraph.query('MATCH (n:Document {name:"'+path+'"}) RETURN n')
        if len(result.result_set) > 0:
            return True
        return False

    def create_folder(self, path:str):
        """Method to create a folder (no check performed)"""
        self.hybridstore.metagraph.query('MERGE (n:Folder {name:"'+path+'"})')
        parent_folder = dirname(path)
        self.hybridstore.metagraph.query('MATCH (n:Folder {name:"'+parent_folder+'"}), (m:Folder {name:"'+path+'"}) MERGE (n)-[:CONTAINS]->(m)')

    def create_document(self, path:str):
        """Method to create a document (no check performed)"""
        self.hybridstore.metagraph.query('MERGE (n:Document {name:"'+path+'"})')
        parent_folder = dirname(path)
        self.hybridstore.metagraph.query('MATCH (n:Folder {name:"'+parent_folder+'"}), (m:Document {name:"'+path+'"}) MERGE (n)-[:CONTAINS]->(m)')

class VirtualFileSystem(FileSystemUtility):
    """The filesystem for the hybridstore"""
    context: FileSystemContext

    class Config:
        """Configuration for this pydantic object."""
        extra = Extra.forbid
        arbitrary_types_allowed = True
    
    def __init__(
            self,
            hybridstore: RedisGraphHybridStore
        ):
        context = FileSystemContext()
        super().__init__(
            hybridstore = hybridstore,
            context = context
        )
        # Create the root & home directory
        self.hybridstore.metagraph.query('MERGE (:Folder {name:"/"})')
        # Create the home directory
        self.create_folder("/home")
        self.create_folder("/home/user")
        self.create_folder("/home/user/Workspace")