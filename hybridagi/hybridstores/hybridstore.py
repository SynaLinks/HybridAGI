import uuid
import base64
from falkordb import FalkorDB, Graph
from typing import List, Optional, Dict, Any
from ..embeddings.base import BaseEmbeddings

class HybridStore():

    def __init__(
            self,
            index_name: str,
            graph_index: str,
            embeddings: BaseEmbeddings,
            hostname: int = "localhost",
            port: int = 6379,
            username: str = "",
            password: str = "",
            indexed_label: str = "Content",
            wipe_on_start: bool = False,
            ):
        self.hostname = hostname
        self.port = port
        self.username = username
        self.password = password
        self.index_name = index_name
        self.graph_index = graph_index
        self.embeddings = embeddings
        self.indexed_label = indexed_label
        self.wipe_on_start = wipe_on_start
        try:
            self.client = FalkorDB(
                hostname,
                port,
                username = username if username else None,
                password = password if password else None,
            )
            self.hybridstore = self.get_graph(self.graph_index)
            self.hybridstore.query("RETURN 1")
        except Exception as e:
            raise ConnectionError("Failed to connect to FalkorDB database") from e
        if self.wipe_on_start:
            self.clear()
        self.hybridstore = self.get_graph(self.index_name)
        try:
            params = {"dim": self.embeddings.dim}
            self.hybridstore.query(
                "CREATE VECTOR INDEX FOR (c:"+self.indexed_label+
                ") ON (c.embeddings_vector) OPTIONS {dimension:$dim, similarityFunction:'euclidean'}",
                params,
            )
        except Exception:
            pass

    def add_texts(
            self,
            texts: List[str],
            ids: List[str] = [],
            descriptions: List[str] = [],
            metadatas: List[Dict[str, str]] = [],
        ) -> List[str]:
        """Method to add texts"""
        indexes = []
        for idx, text in enumerate(texts):
            content_index = str(uuid.uuid4().hex) if not ids else ids[idx]
            description = text if not descriptions else descriptions[idx]
            metadata = {} if not metadatas else metadatas[idx]
            vector = self.embeddings.embed_text(description)
            params = {"vector": list(vector), "index": content_index}
            self.hybridstore.query(
                "MERGE (n:"+self.indexed_label+" {name:$index, embeddings_vector:vecf32($vector)})",
                params,
            )
            self.set_content(content_index, text)
            if descriptions:
                self.set_content_description(content_index, description)
            if metadata:
                self.set_content_metadata(content_index, metadata)
            indexes.append(content_index)
        return indexes

    def get_graph(self, graph_index: str) -> Graph:
        """Retreive a graph from the KB"""
        return self.client.select_graph(self.index_name+":graph:"+graph_index)

    def exists(self, index:str, label:str = "") -> bool:
        """Method to check if an entry is present in the hybridstore"""
        params = {"index": index}
        if label:
            result = self.hybridstore.query(
                'MATCH (n:'+label+' {name:$index}) RETURN n',
                params = params,
            )
        else:
            result = self.hybridstore.query(
                'MATCH (n:'+self.indexed_label+' {name:$index}) RETURN n',
                params = params,
            )
        if len(result.result_set) > 0:
            return True
        return False

    def remove_texts(self, indexes: List[str]):
        """Method to remove texts"""
        for idx in indexes:
            self.delete_content(idx)

    def set_content(self, content_index: str, text: str) -> bool:
        """Set content into FalkorDB"""
        encoded_content = base64.b64encode(text.encode("ascii")).decode("ascii")
        if not self.exists(content_index):
            params = {"index": content_index, "content": encoded_content}
            self.hybridstore.query(
                'MERGE (n:'+self.indexed_label+' {name:$index, content:$content})',
                params = params,
            )
        else:
            params = {"index": content_index, "content": encoded_content}
            self.hybridstore.query(
                'MATCH (n:'+self.indexed_label+' {name:$index}) SET n.content=$content',
                params = params,
            )
        return True

    def get_content(self, content_index: str) -> str:
        """Get content from FalkorDB"""
        if self.exists(content_index):
            params = {"index": content_index}
            result = self.hybridstore.query(
                'MATCH (n:Content {name:$index}) RETURN n.content AS content',
                params=params,
            )
            if len(result.result_set) > 0:
                encoded_content = result.result_set[0][0]
                decoded_content = base64.b64decode(encoded_content.encode("ascii")).decode("ascii")
                return decoded_content
        return ""

    def set_content_description(
            self,
            content_index: str,
            description: str,
        ) -> bool:
        """Method to get the description"""
        if not self.exists(content_index):
            return False
        try:
            params = {"index": content_index, "description": description}
            self.hybridstore.query(
                'MATCH (n:'+self.indexed_label+' {name:$index})'+
                ' SET n.description=$description',
                params = params,
            )
        except Exception:
            return False
        return True

    def get_content_description(self, content_index: str) -> Optional[str]:
        """Method to get the description"""
        if not self.exists(content_index):
            return None
        try:
            params = {"index": content_index}
            result = self.hybridstore.query(
                'MATCH (n:'+self.indexed_label+' {name:$index})'+
                ' RETURN n.description AS description',
                params = params,
            )
            return result.result_set[0][0]
        except Exception:
            return None

    def set_content_metadata(
            self,
            content_index: str,
            metadata: Dict[str, Any],
        ) -> bool:
        """Method to set the content metadata"""
        if not self.exists(content_index):
            return False
        for key, value in metadata.items():
            try:
                params = {"index": content_index, "value": value}
                self.hybridstore.query(
                    'MATCH (n:'+self.indexed_label+' {name:$index})'
                    +' SET n.'+str(key)+'=$value',
                    params = params,
                )
            except Exception:
                return False
        return True

    def get_content_metadata(self, content_index: str) -> Optional[Dict[Any, Any]]:
        """Method to get the description"""
        if not self.exists(content_index):
            return None
        try:
            params = {"index": content_index}
            result = self.hybridstore.query(
                'MATCH (n:'+self.indexed_label+' {name:$index}) RETURN n',
                params = params,
            )
            metadata = result.result_set[0][0].properties
            if "name" in metadata:
                del metadata["name"]
            if "embeddings_vector" in metadata:
                del metadata["embeddings_vector"]
            if "description" in metadata:
                del metadata["description"]
            if "content" in metadata:
                del metadata["content"]
            return metadata
        except Exception:
            return None
        return None

    def delete_content(self, content_index: str) -> bool:
        """Method to delete an entry"""
        if not self.exists(content_index):
            return False
        params = {"index": content_index}
        self.hybridstore.query(
            'MATCH (n:'+self.indexed_label+' {name:$index}) DELETE n',
            params = params)
        return True
        
    def clear(self):
        """Method to clear the entire database"""
        self.client.connection.flushall()