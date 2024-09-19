from typing import Union, List, Optional, Dict, Any
import json
from uuid import UUID
from falkordb import FalkorDB, Graph
from hybridagi.embeddings.embeddings import Embeddings

class FalkorDBMemory():
    """
    The base class for FalkorDB-based memory stores.

    This class provides core functionality for interacting with FalkorDB,
    including initialization of the database connection, graph selection,
    index creation, and basic operations like checking existence and clearing data.

    It serves as a foundation for more specialized memory classes that implement
    specific types of memory (e.g., fact memory, document memory) using FalkorDB
    as the underlying storage system.

    Attributes:
        hostname (str): The hostname of the FalkorDB server.
        port (int): The port number of the FalkorDB server.
        username (str): The username for authentication (if required).
        password (str): The password for authentication (if required).
        index_name (str): The name of the index used for storage.
        graph_index (str): The identifier for the specific graph within the index.
        indexed_label (str): The label used for indexing nodes in the graph.
        wipe_on_start (bool): Whether to clear the memory when initializing.
        client (FalkorDB): The FalkorDB client instance.
        _graph (Graph): The graph object representing the selected or created graph.
    """
    def __init__(
            self,
            index_name: str,
            graph_index: str,
            hostname: str = "localhost",
            port: int = 6379,
            username: str = "",
            password: str = "",
            wipe_on_start: bool = False,
        ):
        self.hostname = hostname
        self.port = port
        self.username = username
        self.password = password
        self.index_name = index_name
        self.graph_index = graph_index
        self.wipe_on_start = wipe_on_start
        self.client = FalkorDB(
            hostname,
            port,
            username = username if username else None,
            password = password if password else None,
        )
        self._graph = self.get_graph(self.graph_index)
        if self.wipe_on_start:
            self.clear()
            
    def exist(self, index: Union[UUID, str], label:str) -> bool:
        query = "MATCH (n:"+label+" {id: $index}) RETURN n"
        result = self._graph.query(query, params={"index": str(index)})
        return len(result.result_set) > 0

    def get_graph(self, graph_index: str) -> Graph:
        """
        Retrieve or create a graph from the FalkorDB knowledge base.

        Args:
            graph_index (str): A unique identifier for the specific graph within the index.

        Returns:
            Graph: A FalkorDB Graph object representing the selected or created graph.
        """
        return self.client.select_graph(self.index_name+":"+graph_index)

    def clear(self):
        """
        Clear all data from the hybridstore.

        This method attempts to delete all nodes and relationships in the graph,
        effectively resetting the memory to an empty state. If the graph is already empty,
        it skips the deletion step.

        Note: This operation is irreversible and should be used with caution.
        """
        try:
            self._graph.delete()
        except Exception as e:
            pass