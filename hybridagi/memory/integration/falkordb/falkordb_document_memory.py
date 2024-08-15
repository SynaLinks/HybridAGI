from typing import Union, List
import uuid
from uuid import UUID
from hybridagi.embeddings.embeddings import Embeddings
from hybridagi.memory.document_memory import DocumentMemory
from hybridagi.core.datatypes import Document, DocumentList
from .falkordb_memory import FalkorDBMemory

def is_valid_uuid(val):
    try:
        uuid.UUID(str(val))
        return True
    except ValueError:
        return False

class FalkorDBDocumentMemory(FalkorDBMemory, DocumentMemory):
    """
    A class used to manage and store documents using FalkorDB.

    This class extends FalkorDBMemory and implements the DocumentMemory interface,
    providing a robust solution for storing and managing documents in a graph database.
    It allows for efficient storage, retrieval, and manipulation of documents using
    FalkorDB's graph capabilities.
    """
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
        self.schema = ""

    def exist(self, doc_id) -> bool:
        """
        Check if a document with the given ID exists in the database.

        Args:
            doc_id: The ID of the document to check for existence.

        Returns:
            bool: True if the document exists, False otherwise.
        """
        result = self.hybridstore.query(
            "MATCH (d:Document {id: $id}) RETURN COUNT(d) AS count",
            params={"id": str(doc_id)}
        )
        return result.result_set[0][0] > 0

    def update(self, doc_or_docs: Union[Document, DocumentList]) -> None:
        """
        Update one or more documents in the database.

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
        """
        if isinstance(doc_or_docs, Document):
            documents = DocumentList(docs=[doc_or_docs])
        elif isinstance(doc_or_docs, DocumentList):
            documents = doc_or_docs
        else:
            raise ValueError("Invalid datatype provided must be Document or DocumentList")

        for doc in documents.docs:
            params = {
                "id": str(doc.id),
                "text": doc.text,
                "parent_id": str(doc.parent_id) if doc.parent_id else None,
                "vector": list(doc.vector) if doc.vector is not None else None
            }
            self.hybridstore.query(
                "MERGE (d:Document {id: $id}) "
                "SET d.text = $text, d.parent_id = $parent_id, d.vector = $vector",
                params=params
            )
            if doc.parent_id:
                self.hybridstore.query(
                    "MATCH (d:Document {id: $id}), (p:Document {id: $parent_id}) "
                    "MERGE (d)-[:PART_OF]->(p)",
                    params=params
                )

    def remove(self, id_or_ids: Union[UUID, str, List[Union[UUID, str]]]) -> None:
        """
        Remove one or more documents from the database.

        This method deletes documents with the specified ID(s) from the database.
        It can handle a single ID or a list of IDs.

        Args:
            id_or_ids (Union[UUID, str, List[Union[UUID, str]]]): The ID(s) of the document(s) to remove.
                Can be a single UUID, string, or a list of UUIDs or strings.

        Note:
            - If a document with the given ID doesn't exist, no error is raised.
            - The DETACH DELETE operation ensures that all relationships of the document are also removed.
        """
        ids = [str(id_or_ids)] if isinstance(id_or_ids, (UUID, str)) else [str(id) for id in id_or_ids]
        for id in ids:
            self.hybridstore.query(
                "MATCH (d:Document {id: $id}) DETACH DELETE d",
                params={"id": id}
            )

    def get(self, id_or_ids: Union[UUID, str, List[Union[UUID, str]]]) -> DocumentList:
        """
        Retrieve one or more documents from the database by their ID(s).

        This method fetches documents with the specified ID(s) from the database.
        It can handle a single ID or a list of IDs.

        Args:
            id_or_ids (Union[UUID, str, List[Union[UUID, str]]]): The ID(s) of the document(s) to retrieve.
                Can be a single UUID, string, or a list of UUIDs or strings.

        Returns:
            DocumentList: A list of Document objects matching the given ID(s).

        Note:
            - If a document with a given ID doesn't exist, it will not be included in the result.
            - The method returns all available fields for each document (id, text, parent_id, vector).
        """
        ids = [str(id_or_ids)] if isinstance(id_or_ids, (UUID, str)) else [str(id) for id in id_or_ids]
        result = self.hybridstore.query(
            "MATCH (d:Document) WHERE d.id IN $ids "
            "RETURN d.id, d.text, d.parent_id, d.vector",
            params={"ids": ids}
        )
        documents = DocumentList()
        for row in result.result_set:
            doc = Document(
                id=UUID(row[0]['id']) if is_valid_uuid(row[0]['id']) else row[0]['id'],
                text=row[0]['text'],
                parent_id=UUID(row[0]['parent_id']) if row[0]['parent_id'] and is_valid_uuid(row[0]['parent_id']) else row[0]['parent_id'],
                vector=row[0]['vector']
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
                id=UUID(row[0]['id']) if is_valid_uuid(row[0]['id']) else row[0]['id'],
                text=row[0]['text'],
                parent_id=UUID(row[0]['parent_id']) if row[0]['parent_id'] and is_valid_uuid(row[0]['parent_id']) else row[0]['parent_id'],
                vector=row[0]['vector']
            )
            documents.docs.append(doc)
        return documents

    def clear(self):
        """
        Clear all documents from the database.

        This method removes all Document nodes and their relationships from the graph database.

        Note:
            - This operation is irreversible and will delete all document data.
            - Use with caution as it will empty the entire document store.
        """
        self.hybridstore.query("MATCH (n:Document) DETACH DELETE n", params={})
