"""The hybridstore. Copyright (C) 2023 SynaLinks. License: GPL-3.0"""
import uuid
import redis
import numpy as np
from pydantic.v1 import BaseModel, Extra
from redis.commands.graph import Graph
from typing import Optional, Dict, Any, List, Callable
from langchain.schema.embeddings import Embeddings
from langchain.graphs.falkordb_graph import FalkorDBGraph

def _default_norm(value):
    return value

class KnowledgeGraph(FalkorDBGraph):
    """The KnowledgeGraph class wrapper"""
    def __init__(
            self,
            client: redis.Redis,
            graph_index: str,
            index_name: str):
        self._driver = client
        self._graph = Graph(self._driver, index_name+":graph:"+graph_index)
        self.name = graph_index
        self.index_name = index_name
        self.schema = ""
        self.structured_schema: Dict[str, Any] = {}
        try:
            self.refresh_schema()
        except Exception as e:
            raise ValueError(f"Could not refresh schema. Error: {e}")
    
    def delete(self):
        self._graph.delete()

class BaseHybridStore(BaseModel):
    """Base class for hybridstores"""
    client: redis.Redis
    index_name: str

    embeddings: Embeddings
    embeddings_dim: int

    graph_index:str
    indexed_label: str

    hybridstore: Optional[KnowledgeGraph] = None

    normalize: Optional[Callable[[Any], Any]] = _default_norm
    verbose: bool = True

    class Config:
        """Configuration for this pydantic object."""
        extra = Extra.allow
        arbitrary_types_allowed = True

    def __init__(
        self,
        redis_url: str,
        index_name: str,
        embeddings: Embeddings,
        embeddings_dim: int,
        graph_index: str,
        indexed_label: str = "Content",
        normalize: Optional[Callable[[Any], Any]] = _default_norm,
        verbose: bool = True,
        ):
        """Base hybridstore constructor"""
        super().__init__(
            client = redis.from_url(redis_url, db=0),
            index_name = index_name,
            embeddings = embeddings,
            embeddings_dim = embeddings_dim,
            graph_index = graph_index,
            indexed_label = indexed_label,
            normalize = normalize,
            verbose = verbose,
        )
        self.hybridstore = self.create_graph(graph_index)

    def similarity_search(
            self,
            query: str,
            k: int = 1,
            fetch_content: bool = False) -> List[str]:
        """Method to perform a similarity search in the hybridstore"""
        vector = self.normalize(np.array(self.embeddings.embed_query(query), dtype=np.float32))
        result = self.query(
            'CALL db.idx.vector.queryNodes('+
            '"'+self.indexed_label+'", '+
            '"embeddings_vector", '+
            str(k)+', '+
            'vecf32('+str(list(vector))+
            ')) YIELD node RETURN node.name AS name')
        final_result = []
        for record in result:
            if fetch_content:
                final_result.append(self.get_content(record[0]))
            else:
                final_result.append(record[0])
        return final_result

    def add_texts(
            self,
            texts: List[str],
            ids: List[str] = [],
            descriptions: List[str] = [],
            metadatas: List[Dict[str, str]] = [],
        ):
        """Method to add texts"""
        indexes = []
        for idx, text in enumerate(texts):
            content_index = str(uuid.uuid4().hex) if not ids else ids[idx]
            description = text if not descriptions else descriptions[idx]
            metadata = {} if not metadatas else metadatas[idx]
            vector = self.normalize(np.array(self.embeddings.embed_query(description), dtype=np.float32))
            self.query(
                'MERGE (n:'+self.indexed_label+' {name:"'+content_index+'"'+
                ', embeddings_vector:vecf32('+str(list(vector))+')})')
            self.set_content(content_index, text)
            if descriptions:
                self.set_content_description(content_index, description)
            if metadata:
                self.set_content_metadata(content_index, metadata)
            indexes.append(content_index)
        return indexes

    def remove_texts(self, indexes: List[str]):
        """Method to remove texts"""
        for idx in indexes:
            self.delete_content(idx)

    def create_graph(self, graph_index: str = "") -> KnowledgeGraph:
        """Method to create a graph client"""
        graph_index = str(uuid.uuid4()) if not graph_index else graph_index
        graph = KnowledgeGraph(
            client = self.client,
            graph_index = graph_index,
            index_name = self.index_name)
        return graph

    def remove_graph(self, graph_index: str) -> bool:
        """Method to remove a graph"""
        return self.client.graph(self.index_name+":graph:"+graph_index).delete()

    def exists(self, index:str) -> bool:
        """Method to check if an entry is present in the hybridstore"""
        result = self.hybridstore.query(
            'MATCH (n:'+self.indexed_label+' {name:"'+index+'"}) RETURN n')
        if len(result) > 0:
            return True
        return False

    def set_content(self, content_index: str, text: str) -> bool:
        """Set content into Redis"""
        if not self.exists(content_index):
            self.query('MERGE (n:'+self.indexed_label+' {name:"'+content_index+'"})')
        return self.client.set(self.index_name+":content:"+content_index, text)

    def get_content(self, content_index: str) -> Optional[str]:
        """Get content from Redis"""
        result = self.client.get(self.index_name+":content:"+content_index)
        return result.decode('utf-8') if result else None

    def set_content_description(
            self,
            content_index: str,
            description: str,
        ) -> bool:
        """Method to get the description"""
        if not self.exists(content_index):
            return False
        try:
            self.query(
                'MATCH (n:'+self.indexed_label+' {name:"'+content_index+'"})'+
                ' SET n.description="'+description+'"'
            )
        except Exception:
            return False
        return True

    def get_content_description(self, content_index: str) -> Optional[str]:
        """Method to get the description"""
        if not self.exists(content_index):
            return None
        try:
            result = self.query(
                'MATCH (n:'+self.indexed_label+' {name:"'+content_index+'"})'+
                ' RETURN n.description AS description')
            return result[0][0]
        except Exception:
            return None

    def set_content_metadata(
            self,
            content_index: str,
            metadata: Dict[str, str],
        ) -> bool:
        if not self.exists(content_index):
            return False
        
        for key, value in metadata.items():
            try:
                self.query(
                    'MATCH (n:'+self.indexed_label+' {name:"'+content_index+'"})'
                    +' SET n.'+str(key)+'='+repr(value))
            except Exception:
                return False
        return True

    def get_content_metadata(self, content_index: str) -> Optional[Dict[Any, Any]]:
        """Method to get the description"""
        if not self.exists(content_index):
            return None
        try:
            result = self.query(
                'MATCH (n:'+self.indexed_label+' {name:"'+content_index+'"})'+
                ' RETURN n')
            metadata = result[0][0].properties
            if "name" in metadata:
                del metadata["name"]
            if "embeddings_vector" in metadata:
                del metadata["embeddings_vector"]
            if "description" in metadata:
                del metadata["description"]
            return metadata
        except Exception as e:
            return e
            return None
        return None

    def delete_content(self, content_index: str) -> bool:
        """Method to delete an entry"""
        return self.client.delete(self.index_name+":content:"+content_index)

    def query(self, query: str) -> List:
        """Method to query the filesystem graph"""
        return self.hybridstore.query(query)

    def initialize(self):
        """Method to initialize the vector index enabling similarity search"""
        try:
            self.query(
                'CREATE VECTOR INDEX FOR (c:'+self.indexed_label+
                ') ON (c.embeddings_vector) OPTIONS {dimension:'+
                str(self.embeddings_dim)+', similarityFunction:"euclidean"}')
        except Exception:
            pass

    def clear(self):
        """Clear the entire database"""
        self.client.flushall()