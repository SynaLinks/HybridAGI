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
    """

    def __init__(
        self,
        index_name: str,
        graph_index: str = "filesystem",
        hostname: str = "localhost",
        port: int = 6379,
        username: str = "",
        password: str = "",
        wipe_on_start: bool = False,
    ):
        super().__init__(
            index_name = index_name,
            graph_index = graph_index,
            hostname = hostname,
            port = port,
            username = username,
            password = password,
            wipe_on_start = wipe_on_start,
        )
        if wipe_on_start:
            self.clear()

    def exist(self, doc_id: Union[UUID, str]) -> bool:
        """
        Check if a document with the given id exists in the database.

        Args:
            doc_id: The id of the document to check for existence.

        Returns:
            bool: True if the document exists, False otherwise.
        """
        return super().exist(doc_id, "Document")

    def update(self, doc_or_docs: Union[Document, DocumentList]) -> None:
        """
        Update one or more documents in the database and local cache.

        This method updates existing documents or creates new ones if they don't exist.
        It handles both individual Document objects and DocumentList objects.

        Args:
            doc_or_docs (Union[Document, DocumentList]): The document(s) to update or create.

        Raises:
            ValueError: If the input is neither a Document nor a DocumentList.
        """
        if not isinstance(doc_or_docs, (Document, DocumentList)):
            raise ValueError("Invalid datatype provided must be Document or DocumentList")
        if isinstance(doc_or_docs, Document):
            documents = DocumentList()
            documents.docs = [doc_or_docs]
        else:
            documents = doc_or_docs
        for doc in documents.docs:
            doc_id = str(doc.id)
            params = {
                "id": doc_id,
                "parent_id": str(doc.parent_id) if doc.parent_id else None,
                "text": doc.text,
                "vector": list(doc.vector) if doc.vector is not None else None,
                "metadata": json.dumps(doc.metadata)
            }
            self._graph.query(
                " ".join([
                "MERGE (d:Document {id: $id})",
                "SET",
                "d.text=$text,",
                "d.parent_id=$parent_id,",
                "d.metadata=$metadata,",
                "d.vector=vecf32($vector)"]),
                params = params,
            )
            params = {
                "id": doc_id,
            }
            self._graph.query(
                "MATCH (:Document {id: $id})-[r]->() DELETE r",
                params=params,
            )
            if doc.parent_id is not None:
                parent_id = str(doc.parent_id)
                params = {
                    "id": doc_id,
                    "parent_id": parent_id,
                }
                self._graph.query(
                    " ".join([
                    "MATCH (d:Document {id: $id})",
                    "MERGE (d)-[:PART_OF]->(:Document {id: $parent_id})"]),
                    params = params,
                )

    def remove(self, id_or_ids: Union[UUID, str, List[Union[UUID, str]]]) -> None:
        """
        Remove one or more documents from the database.

        This method deletes documents with the specified ID(s) from the database.
        It can handle a single document ID or a list of document IDs.

        Args:
            doc_or_docs (Union[UUID, str, List[Union[UUID, str]]]): The ID(s) of the document(s) to remove.
                Can be a single UUID, string, or a list of UUIDs or strings.
        """
        if not isinstance(id_or_ids, list):
            documents_ids = [id_or_ids]
        else:
            documents_ids = id_or_ids
        for doc_id in documents_ids:
            doc_id = str(doc_id)
            self._graph.query(
                "MATCH (n:Document {id: $id}) DETACH DELETE n",
                params={"id": doc_id}
            )

    def get(self, id_or_ids: Union[UUID, str, List[Union[UUID, str]]]) -> DocumentList:
        """
        Retrieve one or more documents from the database by their ID(s).

        This method fetches documents with the specified ID(s) from the database.
        It can handle a single ID or a list of IDs, which can be UUIDs or strings.

        Args:
            id_or_ids (Union[UUID, str, List[Union[UUID, str]]]): The ID(s) of the document(s) to retrieve.
                Can be a single UUID, string, or a list of UUIDs or strings.

        Returns:
            DocumentList: A list of Document objects matching the given ID(s).

        Note:
            - If a document with a given ID doesn't exist, it will not be included in the result.
            - The method returns all available fields for each document (id, text, parent_id, vector, metadata).
        """
        if not isinstance(id_or_ids, list):
            documents_ids = [id_or_ids]
        else:
            documents_ids = id_or_ids
        result = DocumentList()
        for doc_id in documents_ids:
            doc_id = str(doc_id)
            if self.exist(doc_id):
                query_result = self._graph.query(
                    "MATCH (d:Document {id: $id}) RETURN d",
                    params={"id": doc_id}
                )
                text = query_result.result_set[0][0].properties["text"]
                metadata = query_result.result_set[0][0].properties["metadata"]
                if "parent_id" in query_result.result_set[0][0].properties:
                    parent_id = query_result.result_set[0][0].properties["parent_id"]
                else:
                    parent_id = None
                if parent_id:
                    try:
                        parent_id = UUID(parent_id)
                    except Exception:
                        pass
                else:
                    parent_id = None
                try:
                    doc_id = UUID(doc_id)
                except Exception:
                    pass
                doc = Document(id=doc_id, parent_id=parent_id, text=text)
                doc.metadata = json.loads(metadata)
                if "vector" in query_result.result_set[0][0].properties:
                    doc.vector = query_result.result_set[0][0].properties["vector"]
                result.docs.append(doc)
        return result

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
        """
        if not isinstance(id_or_ids, list):
            documents_ids = [id_or_ids]
        result = DocumentList()
        parent_ids = []
        for doc in self.get(documents_ids):
            if doc.parent_id:
                parent_ids.append(doc.parent_id)
        return self.get(parent_ids)