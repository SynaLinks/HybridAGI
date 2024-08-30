from typing import Union, List, Optional, Dict, Any, Tuple
from uuid import UUID
from collections import OrderedDict
import json
from .falkordb_memory import FalkorDBMemory
from ....embeddings.embeddings import Embeddings
from ....memory.document_memory import DocumentMemory
from ....core.datatypes import DocumentList, Document
from ....core.datatypes import GraphProgramList
from falkordb import Node, Graph

class FalkorDBDocumentMemory(FalkorDBMemory, DocumentMemory):
    """
    A class used to manage and store documents using FalkorDB.

    This class extends FalkorDBMemory and implements the DocumentMemory interface,
    providing a robust solution for storing and managing documents in a graph database.
    It allows for efficient storage, retrieval, and manipulation of documents using
    FalkorDB's graph capabilities.

    Attributes:
        _documents (Optional[Dict[str, Document]]): A dictionary to store documents.
            The keys are document IDs and the values are Document objects.
        _embeddings (Optional[Dict[str, List[float]]]): An ordered dictionary to store document embeddings.
            The keys are document IDs and the values are lists of floats representing the embeddings.
    """
    _documents: Optional[Dict[str, Document]] = {}
    _embeddings: Optional[Dict[str, List[float]]] = OrderedDict()

    def __init__(
        self,
        index_name: str,
        embeddings: Embeddings,
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
        self._embeddings_model = embeddings
        self.schema = ""
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        if wipe_on_start:
            self.clear()
        self.init()

    def init(self):
        """Method to initialize the filesystem"""
        self.hybridstore.query('MERGE (:Folder {name:"/"})')
        folders = [
            "/home",
            "/home/user",
            "/home/user/Downloads",
            "/home/user/Documents",
            "/home/user/Pictures",
            "/home/user/Music"
        ]
        for folder in folders:
            self.create_folder(folder)

    def create_folder(self, path: str):
        """Create a folder in the filesystem"""
        parts = path.strip('/').split('/')
        current_path = "/"
        for part in parts:
            next_path = current_path + part if current_path == "/" else current_path + "/" + part
            self.hybridstore.query(
                'MATCH (parent:Folder {name: $parent_path}) '
                'MERGE (parent)-[:CONTAINS]->(folder:Folder {name: $folder_name})',
                params={"parent_path": current_path, "folder_name": next_path}
            )
            current_path = next_path

    def exist(self, doc_name: str) -> bool:
        """
        Check if a document with the given name exists in the database.

        Args:
            doc_name: The name of the document to check for existence.

        Returns:
            bool: True if the document exists, False otherwise.
        """
        return super().exist(doc_name, "Document")

    def update(self, doc_or_docs: Union[Document, DocumentList]) -> None:
        """
        Update one or more documents in the database and local cache.

        This method updates existing documents or creates new ones if they don't exist.
        It handles both individual Document objects and DocumentList objects.

        Args:
            doc_or_docs (Union[Document, DocumentList]): The document(s) to update or create.

        Raises:
            ValueError: If the input is neither a Document nor a DocumentList.

        Note:
            - If a document with the given ID already exists, it will be updated.
            - If a document with the given ID doesn't exist, a new one will be created.
            - For documents with a parent_id, a PART_OF relationship is created or updated.
            - If a document doesn't have a vector, it will be generated using the text content.
            - The local cache (_documents and _embeddings) is updated along with the database.
            - Documents are added to the /home/user/Documents folder in the filesystem structure.
            - Document metadata is stored as properties on the Document node.
        """
        if isinstance(doc_or_docs, Document):
            documents = DocumentList(docs=[doc_or_docs])
        elif isinstance(doc_or_docs, DocumentList):
            documents = doc_or_docs
        else:
            raise ValueError("Invalid datatype provided must be Document or DocumentList")

        for doc in documents.docs:
            # Generate vector if not provided
            if doc.vector is None:
                doc.vector = self._embeddings_model.embed_text(doc.text)

            doc_id = str(doc.id)
            params = {
                "id": doc_id,
                "text": doc.text,
                "parent_id": str(doc.parent_id) if doc.parent_id else None,
                "vector": list(doc.vector),
                "name": doc_id,  # Using id as name for consistency
                "metadata": json.dumps(doc.metadata) if doc.metadata else "{}"
            }
            
            # Create or update the document node
            self.hybridstore.query(
                "MERGE (d:Document {id: $id}) "
                "SET d.text = $text, d.parent_id = $parent_id, d.vector = $vector, d.name = $name, "
                "d.metadata = $metadata",
                params=params
            )
            
            # Create relationship with parent document if parent_id exists
            if doc.parent_id:
                self.hybridstore.query(
                    "MATCH (d:Document {id: $id}), (p:Document {id: $parent_id}) "
                    "MERGE (d)-[:PART_OF]->(p)",
                    params=params
                )
            
            # Add the document to the /home/user/Documents folder
            self.hybridstore.query(
                "MATCH (d:Document {id: $id}), (f:Folder {name: '/home/user/Documents'}) "
                "MERGE (f)-[:CONTAINS]->(d)",
                params=params
            )

            # Update local cache
            self._documents[doc_id] = doc
            self._embeddings[doc_id] = doc.vector

    def remove(self, doc_or_docs: Union[UUID, str, List[Union[UUID, str]]]) -> None:
        """
        Remove one or more documents from the database and local cache.

        This method deletes documents with the specified ID(s) from the database and local cache.
        It can handle a single document ID or a list of document IDs.

        Args:
            doc_or_docs (Union[UUID, str, List[Union[UUID, str]]]): The ID(s) of the document(s) to remove.
                Can be a single UUID, string, or a list of UUIDs or strings.

        Note:
            - If a document with the given ID doesn't exist, no error is raised.
            - The DETACH DELETE operation ensures that all relationships of the document are also removed.
            - The document is also removed from the local cache (_documents and _embeddings).
        """
        ids = [str(doc_or_docs)] if isinstance(doc_or_docs, (UUID, str)) else [str(id) for id in doc_or_docs]
        super().remove(ids, label="Document")

        # Remove from local cache
        for id in ids:
            self._documents.pop(id, None)
            self._embeddings.pop(id, None)

    def get(self, doc_or_docs: Union[UUID, str, List[Union[UUID, str]]]) -> DocumentList:
        """
        Retrieve one or more documents from the database by their ID(s).

        This method fetches documents with the specified ID(s) from the database.
        It can handle a single ID or a list of IDs, which can be UUIDs or strings.

        Args:
            doc_or_docs (Union[UUID, str, List[Union[UUID, str]]]): The ID(s) of the document(s) to retrieve.
                Can be a single UUID, string, or a list of UUIDs or strings.

        Returns:
            DocumentList: A list of Document objects matching the given ID(s).

        Note:
            - If a document with a given ID doesn't exist, it will not be included in the result.
            - The method returns all available fields for each document (id, text, parent_id, vector, metadata).
        """
        ids = [str(doc_or_docs)] if isinstance(doc_or_docs, (UUID, str)) else [str(id) for id in doc_or_docs]
        result = self.hybridstore.query(
            "MATCH (d:Document) WHERE d.id IN $ids "
            "RETURN d.id AS id, d.text AS text, d.parent_id AS parent_id, d.vector AS vector, d.metadata AS metadata",
            params={"ids": ids}
        )
        documents = DocumentList()
        for row in result.result_set:
            doc = Document(
                id=UUID(row[0]) if row[0] else row[0],
                text=row[1],
                parent_id=UUID(row[2]) if row[2] else row[2],
                vector=row[3],
                metadata=json.loads(row[4]) if row[4] else None
            )
            documents.docs.append(doc)
        return documents

    def get_parents(self, id_or_ids: Union[UUID, str, List[Union[UUID, str]]]) -> DocumentList:
        """
        Retrieve the parent documents of one or more documents from the database.

        This method fetches the parent documents of the specified document(s) based on their ID(s).
        It can handle a single ID or a list of IDs.

        Args:
            id_or_ids (Union[UUID, str, List[Union[UUID, str]]]): The ID(s) of the document(s) whose parents are to be retrieved.
                Can be a single UUID, string, or a list of UUIDs or strings.

        Returns:
            DocumentList: A list of Document objects representing the parent documents.

        Note:
            - If a document with a given ID doesn't exist or doesn't have a parent, it will not be included in the result.
            - The method returns all available fields for each parent document (id, text, parent_id, vector).
            - The PART_OF relationship is used to determine the parent-child relationship between documents.
        """
        ids = [str(id_or_ids)] if isinstance(id_or_ids, (UUID, str)) else [str(id) for id in id_or_ids]
        result = self.hybridstore.query(
            "MATCH (d:Document)-[:PART_OF]->(p:Document) WHERE d.id IN $ids "
            "RETURN p.id, p.text, p.parent_id, p.vector",
            params={"ids": ids}
        )
        documents = DocumentList()
        for row in result.result_set:
            doc = Document(
                id=UUID(row[0]['id']) if row[0]['id'] else row[0]['id'],
                text=row[0]['text'],
                parent_id=UUID(row[0]['parent_id']) if row[0]['parent_id'] else row[0]['parent_id'],
                vector=row[0]['vector']
            )
            documents.docs.append(doc)
        return documents

    def clear(self):
        """
        Clear all documents from the database and reset the local cache.
        """
        super().clear()
        self._documents = {}
        self._embeddings = OrderedDict()
        self.init()

    def search(self, query: str, limit: int = 10) -> DocumentList:
        """
        Search for documents based on a query string.

        Args:
            query (str): The search query.
            limit (int): The maximum number of results to return. Defaults to 10.

        Returns:
            DocumentList: A list of Document objects matching the query.
        """
        query_vector = self._embeddings_model.embed_text(query)
        result = self.hybridstore.query(
            "MATCH (d:Document) "
            "WHERE d.text CONTAINS $query "
            "RETURN d.id, d.text, d.parent_id, d.vector, d.metadata "
            "LIMIT $limit",
            params={"query": query, "limit": limit},
            timeout=None
        )
        documents = DocumentList()
        for row in result.result_set:
            doc = Document(
                id=UUID(row[0]),
                text=row[1],
                parent_id=UUID(row[2]) if row[2] else None,
                vector=row[3],
                metadata=json.loads(row[4]) if row[4] else None
            )
            documents.docs.append(doc)
        return documents

    def get_all(self) -> DocumentList:
        """
        Retrieve all documents from the database.

        Returns:
            DocumentList: A list of all Document objects in the database.
        """
        result = self.hybridstore.query(
            "MATCH (d:Document) "
            "RETURN d.id, d.text, d.parent_id, d.vector"
        )
        documents = DocumentList()
        for row in result.result_set:
            doc = Document(
                id=UUID(row[0]['id']),
                text=row[0]['text'],
                parent_id=UUID(row[0]['parent_id']) if row[0]['parent_id'] else None,
                vector=row[0]['vector']
            )
            documents.docs.append(doc)
        return documents

    def get_children(self, id_or_ids: Union[UUID, str, List[Union[UUID, str]]]) -> DocumentList:
        """
        Retrieve the child documents of one or more documents from the database.

        Args:
            id_or_ids (Union[UUID, str, List[Union[UUID, str]]]): The ID(s) of the document(s) whose children are to be retrieved.

        Returns:
            DocumentList: A list of Document objects representing the child documents.
        """
        ids = [str(id_or_ids)] if isinstance(id_or_ids, (UUID, str)) else [str(id) for id in id_or_ids]
        result = self.hybridstore.query(
            "MATCH (p:Document)<-[:PART_OF]-(c:Document) WHERE p.id IN $ids "
            "RETURN c.id, c.text, c.parent_id, c.vector",
            params={"ids": ids}
        )
        documents = DocumentList()
        for row in result.result_set:
            doc = Document(
                id=UUID(row[0]['id']),
                text=row[0]['text'],
                parent_id=UUID(row[0]['parent_id']) if row[0]['parent_id'] else None,
                vector=row[0]['vector']
            )
            documents.docs.append(doc)
        return documents
