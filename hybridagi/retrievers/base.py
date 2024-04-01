import dspy
import base64
from falkordb import FalkorDB, Graph
from ..embeddings.base import BaseEmbeddings

class BaseRetriever(dspy.Retrieve):

    def __init__(
            self,
            index_name: str,
            graph_index: str,
            embeddings: BaseEmbeddings,
            hostname: str = "localhost",
            port: int = 6379,
            username: str = "",
            password: str = "",
            indexed_label: str = "Content",
            k: int = 3,
        ):
        """The retriever constructor"""
        super().__init__(k=k)
        self.index_name = index_name
        self.graph_index = graph_index
        self.embeddings = embeddings
        self.indexed_label = indexed_label
        self.port = port
        self.hostname = hostname
        self.username = username
        self.password = password
        self.indexed_label = indexed_label
        try:
            self.client = FalkorDB(
                hostname,
                port,
                username = username if username else None,
                password = password if password else None,
            )
            self.hybridstore = self.get_graph(self.index_name)
            self.hybridstore.query("RETURN 1")
        except Exception as e:
            raise ConnectionError("Failed to connect to FalkorDB database") from e
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

    def get_graph(self, graph_index: str) -> Graph:
        """Retreive a graph from the KB"""
        return self.client.select_graph(self.index_name+":graph:"+graph_index)

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