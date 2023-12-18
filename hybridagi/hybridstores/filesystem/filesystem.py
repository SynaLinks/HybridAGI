import os
from typing import Optional, List, Callable, Any, Dict, Union

from .context import FileSystemContext
from .path import join
from .base import BaseFileSystem
from langchain.schema.embeddings import Embeddings
from langchain.text_splitter import (
    RecursiveCharacterTextSplitter,
    Language,
)
from langchain.document_loaders import PyPDFLoader
from langchain.schema import Document
from ..hybridstore import _default_norm

class FileSystem(BaseFileSystem):
    """The File System"""
    def __init__(
            self,
            redis_url: str,
            index_name: str,
            embeddings: Embeddings,
            embeddings_dim: int,
            context: Optional[FileSystemContext] = None,
            normalize: Optional[Callable[[Any], Any]] = _default_norm,
            chunk_size: int = 1500,
            chunk_overlap: int = 0,
            verbose: bool = True):
        """The file system constructor"""
        super().__init__(
            redis_url = redis_url,
            index_name = index_name,
            embeddings = embeddings,
            embeddings_dim = embeddings_dim,
            normalize = normalize,
            verbose = verbose)
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.context = context if context else FileSystemContext()
    
    def add_documents(
            self,
            paths: List[str],
            texts: List[Union[str,Document]],
            languages: List[str] = [],
            metadatas: List[Dict[str, Any]] = [],
        ):
        """Method to add documents"""
        assert(len(texts) == len(paths))
        if languages:
            assert(len(texts) == len(languages))
        for idx, text in enumerate(texts):
            path = paths[idx]
            language = languages[idx] if languages else ""
            metadata = metadatas[idx] if metadatas else {}
            if self.exists(path):
                self.remove_documents([path])
            if language not in [e.value for e in Language]:
                text_splitter = RecursiveCharacterTextSplitter(
                    chunk_size=self.chunk_size,
                    chunk_overlap=self.chunk_overlap)
            else:
                text_splitter = \
                RecursiveCharacterTextSplitter.from_language(
                    language=language,
                    chunk_size=self.chunk_size,
                    chunk_overlap=self.chunk_overlap)
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
            keys = self.add_texts(
                texts = subdocs_texts,
                metadatas = subdocs_metadatas,
            )
            if len(keys) > 0:
                self.create_document(path)
                for i, key in enumerate(keys):
                    self.query(
                        'MATCH (n:Document {name:"'+path+'"}),'+
                        ' (m:Content {name:"'+key+'"}) MERGE (n)-[:CONTAINS]->(m)')
                    if i > 0:
                        self.query(
                            'MATCH (n:Content {name:"'+keys[i-1]+'"}),'+
                            ' (m:Content {name:"'+key+'"}) MERGE (n)-[:NEXT]->(m)')
                self.query(
                    'MATCH (n:Document {name:"'+path+'"}),'+
                    ' (m:Content {name:"'+keys[0]+'"}) MERGE (n)-[:BOF]->(m)')
                self.query(
                    'MATCH (n:Document {name:"'+path+'"}),'+
                    ' (m:Content {name:"'+keys[-1]+'"}) MERGE (n)-[:EOF]->(m)')
    
    def append_documents(
                self,
                paths: List[str],
                texts: List[Union[str,Document]],
                languages: List[str] = [],
                metadatas: List[Dict[str, Any]] = [],
            ):
        """Method to append documents"""
        assert(len(texts) == len(paths))
        if languages:
            assert(len(texts) == len(languages))
        for idx, text in enumerate(texts):
            path = paths[idx]
            language = languages[idx] if languages else ""
            metadata = metadatas[idx] if metadatas else {}
            if not self.exists(path):
                self.add_documents(
                    [path],
                    [text],
                    [language])
            else:
                if language not in [e.value for e in Language]:
                    text_splitter = RecursiveCharacterTextSplitter(
                        chunk_size=self.chunk_size,
                        chunk_overlap=self.chunk_overlap)
                else:
                    text_splitter = \
                    RecursiveCharacterTextSplitter.from_language(
                        language=language,
                        chunk_size=self.chunk_size,
                        chunk_overlap=self.chunk_overlap)
                if isinstance(text, Document):
                    sub_docs = text_splitter.split_documents(
                        [text]
                    )
                elif isinstance(text, str):
                    sub_docs = text_splitter.split_documents(
                        [Document(page_content=text, metadata=metadata)]
                    )
                else:
                    raise ValueError("Parameter texts should be a string or Document")
                subdocs_texts = [d.page_content for d in sub_docs]
                subdocs_metadatas = [d.metadata for d in sub_docs]
                keys = self.add_texts(
                    texts = subdocs_texts,
                    metadatas = subdocs_metadatas,
                )
                eof = self.get_end_of_file(path)
                if len(keys) > 0:
                    for i, key in enumerate(keys):
                        self.query(
                            'MERGE (n:Content {name:"'+key+'"})')
                        self.query(
                            'MATCH (n:Document {name:"'+path+'"}),'+
                            ' (m:Content {name:"'+key+'"}) MERGE (n)-[:CONTAINS]->(m)')
                        if i > 0:
                            self.query(
                                'MATCH (n:Content {name:"'+keys[i-1]+'"}),'+
                                ' (m:Content {name:"'+key+'"}) MERGE (n)-[:NEXT]->(m)')
                    self.query(
                        'MATCH (n:Content {name:"'+eof+'"}),'+
                        ' (m:Content {name:"'+keys[0]+'"}) MERGE (n)-[:NEXT]->(m)')
                    self.query(
                        'MATCH (n:Document {name:"'+path+'"})-[r:EOF]->() DELETE r')
                    self.query(
                        'MATCH (n:Document {name:"'+path+'"}),'+
                        ' (m:Content {name:"'+keys[-1]+'"}) MERGE (n)-[:EOF]->(m)')
    
    def get_document(self, path:str) -> str:
        """
        Method to get the full document.
        Do not use it for the LLM tools as it can exceed the max token.
        """
        if self.exists(path):
            if self.is_folder(path):
                return "Cannot read directory."
        else:
            return "No such file or directory."
        text = ""
        bof = self.get_beginning_of_file(path)
        eof = self.get_end_of_file(path)
        if bof == eof:
            result = self.query(
                'MATCH (n:Content {name:"'+bof+'"}) RETURN n')
            content_key = result[0][0].properties["name"]
            content = self.get_content(content_key)
            text = content
        else:
            result = self.query(
                'MATCH path=(:Content {name:"'+bof+'"})'+
                '-[:NEXT*]->(:Content {name:"'+eof+'"}) RETURN nodes(path)')
            all_content = []
            for node in result[0][0]:
                content_key = node.properties["name"]
                content = self.get_content(content_key)
                all_content.append(content)
            text = "\n".join(all_content)
        return text

    def remove_documents(self, paths: List[str]):
        for path in paths:
            indexes = []
            result = self.query(
                'MATCH (c:Content)<-[:CONTAINS]-(d:Document {name:"'+
                path+'"}) RETURN c.name AS name')
            for record in result:
                indexes.append(record[0])
            self.query(
                'MATCH (c:Content)<-[:CONTAINS]-(d:Document {name:"'+
                path+'"}) DELETE c, d')
            self.remove_texts(indexes)     
            
    def add_folders(
            self,
            folders: List[str],
            folder_names: List[str] = []):
        """Method to add folders"""
        names = []
        docs = []
        for i, folder in enumerate(folders):
            if folder_names is None:
                folder_name = os.path.basename(folder)
            else:
                folder_name = folder_names[i]
            folder_name = self.context.eval_path(folder_name)
            self.create_folder(folder_name)
            for dirpath, dirnames, filenames in os.walk(folder):
                if dirpath.find("__") > 0 or dirpath.find(".git") > 0:
                    continue
                for dir_name in dirnames:
                    if not dir_name.startswith("__") \
                            and not dir_name.startswith(".git"):
                        path = join([dirpath.replace(folder, folder_name), dir_name])
                        self.create_folder(path)
                for filename in filenames:
                    if not filename.startswith(".") and not filename.endswith(".zip"):
                        source = os.path.join(dirpath, filename)
                        try:
                            if filename.endswith(".pdf"):
                                loader = PyPDFLoader(filename, extract_image=True)
                                pages = loader.load_and_split()
                                for idx, p in enumerate(pages):
                                    docs.append(p)
                                    path = join(
                                        [
                                            dirpath.replace(folder, folder_name),
                                            f"page_{idx}_"+filename,
                                        ]
                                    )
                                    names.append(path)
                            else:
                                f = open(source, "r")
                                file_content = f.read()
                                doc = Document(page_content=str(file_content))
                                docs.append(doc)
                                path = join(
                                    [
                                        dirpath.replace(folder, folder_name),
                                        filename,
                                    ]
                                )
                                names.append(path)
                        except Exception:
                            pass
        self.add_documents(names, docs)