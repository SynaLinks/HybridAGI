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

    def exists(self, index: str, label: str = "") -> bool:
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
        if label:
            result = self.hybridstore.query(
                'MATCH (n:' + label + ' {id: $index}) RETURN COUNT(n) AS count',
                params=params,
            )
        else:
            result = self.hybridstore.query(
                'MATCH (n {id: $index}) RETURN COUNT(n) AS count',
                params=params,
            )
        return int(result.result_set[0][0]) > 0

    def clear(self):
        """
        Clear all data from the hybridstore and reinitialize the index.

        This method deletes all nodes and relationships in the graph,
        effectively resetting the memory to an empty state. After clearing
        the data, it reinitializes the index to ensure the graph is ready
        for new data to be added.

        Note: This operation is irreversible and should be used with caution.
        """
        self.hybridstore.delete()
        self.init_index()

    def init_index(self):
        """
        Initialize indexes for efficient querying in FalkorDB.

        This method attempts to create two types of indexes:
        1. A standard index on the 'name' property of nodes with the specified label.
        2. A vector index on the 'embeddings_vector' property for similarity searches.

        The method suppresses exceptions that might occur if the indexes already exist.
        This allows the method to be called safely multiple times without causing errors.

        Note:
        - The standard index is created on the 'name' property of nodes with the label
          specified by self.indexed_label.
        - The vector index is created on the 'embeddings_vector' property, using the
          dimension specified in self.embeddings.dim and the Euclidean similarity function.
        """
        try:
            self.hybridstore.query(f"CREATE INDEX FOR (n:`{self.indexed_label}`) ON (n.name)")
        except Exception:
            pass  # Suppress exception if index already exists

        try:
            params = {"dim": self.embeddings.dim}
            self.hybridstore.query(
                f"CREATE VECTOR INDEX FOR (c:{self.indexed_label}) "
                "ON (c.embeddings_vector) "
                "OPTIONS {dimension:$dim, similarityFunction:'euclidean'}",
                params,
            )
        except Exception:
            pass  # Suppress exception if index already exists
