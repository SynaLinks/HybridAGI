from typing import Union, List, Optional, Dict, Any
import json
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
        embeddings (Embeddings): An instance of the Embeddings class for vector operations.
        indexed_label (str): The label used for indexing nodes in the graph.
        wipe_on_start (bool): Whether to clear the memory when initializing.
        client (FalkorDB): The FalkorDB client instance.
        hybridstore (Graph): The graph object representing the selected or created graph.
    """
    def __init__(
            self,
            index_name: str,
            graph_index: str,
            embeddings: Embeddings,
            hostname: str = "localhost",
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
        self.client = FalkorDB(
            hostname,
            port,
            username = username if username else None,
            password = password if password else None,
        )
        self.hybridstore = self.get_graph(self.graph_index)
        if self.wipe_on_start:
            self.clear()
        self.init_index()


    def get_graph(self, graph_index: str) -> Graph:
        """
        Retrieve or create a graph from the FalkorDB knowledge base.

        This method constructs a unique graph identifier by combining the index_name,
        'graph:', and the provided graph_index. It then uses this identifier to select
        (or create, if it doesn't exist) a graph in the FalkorDB instance.

        Args:
            graph_index (str): A unique identifier for the specific graph within the index.

        Returns:
            Graph: A FalkorDB Graph object representing the selected or created graph.
        """
        return self.client.select_graph(self.index_name+":graph:"+graph_index)

    def exist(self, index: str, label: str = None) -> bool:
        """
        Check if an entry with the given index exists in the graph.

        This method queries the graph to determine if a node with the specified
        index (and optionally, label) exists.

        Args:
            index (str): The unique identifier of the node to check for.
            label (str, optional): The label of the node to check for. If not provided,
                                   the method will check for any node with the given index.

        Returns:
            bool: True if a matching node is found, False otherwise.
        """
        params = {"index": index}
        query = 'MATCH (n {name: $index}) RETURN COUNT(n) AS count'
        if label:
            query = f'MATCH (n:{label} {{name: $index}}) RETURN COUNT(n) AS count'
        result = self.hybridstore.query(query, params=params)
        return int(result.result_set[0][0]) > 0

    def clear(self):
        """
        Clear all data from the hybridstore and reinitialize the index.

        This method attempts to delete all nodes and relationships in the graph,
        effectively resetting the memory to an empty state. If the graph is already empty,
        it skips the deletion step. After clearing the data (or attempting to),
        it reinitializes the index to ensure the graph is ready for new data to be added.

        Note: This operation is irreversible and should be used with caution.
        """
        try:
            self.hybridstore.delete()
        except Exception as e:
            pass
        self.init_index()

    def init_index(self):
        """
        Initialize or ensure the existence of necessary indexes in the graph.

        This method attempts to create two types of indexes:
        1. A standard index on the 'name' property for nodes with the specified label.
        2. A vector index on the 'embeddings_vector' property for nodes with the specified label.

        If the indexes already exist, the creation attempts are silently ignored.

        Note: This method catches and ignores any exceptions during index creation,
        which might hide potential issues. Consider logging these exceptions in a
        production environment.
        """
        try:
            self.hybridstore.query(f"CREATE INDEX FOR (n:`{self.indexed_label}`) ON (n.name)")
        except Exception:
            pass
        try:
            params = {"dim": self.embeddings.dim}
            self.hybridstore.query(
                "CREATE VECTOR INDEX FOR (c:"+self.indexed_label+
                ") ON (c.embeddings_vector) OPTIONS {dimension:$dim, similarityFunction:'euclidean'}",
                params,
            )
        except Exception:
            pass

    def remove(self, id_or_ids: Union[str, List[str]], label: str) -> None:
        """
        Remove a node or a list of nodes by their IDs.

        This method deletes nodes with the specified ID(s) from the database.
        It can handle a single ID or a list of IDs. If a label is provided,
        only nodes with that label will be removed.

        Args:
            id_or_ids (Union[str, List[str]]): The ID(s) of the node(s) to remove.
                Can be a single string or a list of strings.
            label (str): The label of the nodes to remove. If provided,
                         only nodes with this label will be considered for removal.

        Note: This method does not return a value or raise exceptions if nodes are not found.
        """
        ids = [id_or_ids] if isinstance(id_or_ids, str) else id_or_ids
        for id in ids:
            if label:
                self.hybridstore.query(
                    f"MATCH (n:{label} {{name: $name}}) DETACH DELETE n",
                    params={"name": id}
                )
            else:
                self.hybridstore.query(
                    "MATCH (n {name: $name}) DETACH DELETE n",
                    params={"name": id}
                )

    def set_content(self, content_index: str, text: str, label: str) -> bool:
        """
        Set or update content for a node in FalkorDB.

        This method creates a new node or updates an existing one with the given content.
        The node is identified by its content_index and label.

        Args:
            content_index (str): The unique identifier for the node.
            text (str): The content to be stored in the node.
            label (str): The label to be applied to the node.

        Returns:
            bool: True if the operation was successful, False otherwise.
        """
        params = {"index": content_index, "content": text}
        query = f'MERGE (n:{label} {{name:$index}}) SET n.content = $content, n.description = $content RETURN n'
        result = self.hybridstore.query(query, params=params)
        return len(result.result_set) > 0

    def set_content_description(self, content_index: str, description: str, label: str) -> bool:
        """
        Set or update the description of a node in FalkorDB.

        This method updates the description of an existing node identified by its
        content_index and label.

        Args:
            content_index (str): The unique identifier for the node.
            description (str): The description to be set for the node.
            label (str): The label of the node to be updated.

        Returns:
            bool: True if the operation was successful, False otherwise.
        """
        params = {"index": content_index, "description": description}
        query = f"MATCH (n:{label} {{name: $index}}) SET n.description = $description RETURN n"
        result = self.hybridstore.query(query, params=params)
        return len(result.result_set) > 0

    def get_content_description(self, content_index: str, label: str) -> Optional[str]:
        """
        Retrieve the description of a node from FalkorDB.

        This method fetches the description of a node identified by its content_index
        and label. If the description is not set, it returns the content of the node.

        Args:
            content_index (str): The unique identifier for the node.
            label (str): The label of the node to retrieve the description from.

        Returns:
            Optional[str]: The description of the node if found, None otherwise.
        """
        params = {"index": content_index}
        query = f"MATCH (n:{label} {{name: $index}}) RETURN COALESCE(n.description, n.content)"
        result = self.hybridstore.query(query, params=params)
        return result.result_set[0][0] if result.result_set else None

    def set_content_metadata(self, content_index: str, metadata: Dict[Any, Any], label: str) -> bool:
        """
        Set or update the metadata of a node in FalkorDB.

        This method updates the metadata of an existing node identified by its
        content_index and label. The metadata is stored as a JSON string.

        Args:
            content_index (str): The unique identifier for the node.
            metadata (Dict[Any, Any]): A dictionary containing the metadata to be stored.
            label (str): The label of the node to be updated.

        Returns:
            bool: True if the operation was successful, False otherwise.
        """
        params = {"index": content_index, "metadata": json.dumps(metadata)}
        query = f"MATCH (n:{label} {{name: $index}}) SET n.metadata = $metadata RETURN n"
        result = self.hybridstore.query(query, params=params)
        return len(result.result_set) > 0

    def get_content_metadata(self, content_index: str, label: str) -> Optional[Dict[Any, Any]]:
        """
        Retrieve the metadata of a node from FalkorDB.

        This method fetches the metadata of a node identified by its content_index
        and label. The metadata is stored as a JSON string and is parsed into a dictionary.

        Args:
            content_index (str): The unique identifier for the node.
            label (str): The label of the node to retrieve the metadata from.

        Returns:
            Optional[Dict[Any, Any]]: The metadata of the node as a dictionary if found,
                                      None otherwise.
        """
        params = {"index": content_index}
        query = f"MATCH (n:{label} {{name: $index}}) RETURN n.metadata"
        result = self.hybridstore.query(query, params=params)
        return json.loads(result.result_set[0][0]) if result.result_set and result.result_set[0][0] else None
