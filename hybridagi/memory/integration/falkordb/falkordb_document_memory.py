from typing import Union, List
from uuid import UUID
from hybridagi.memory.document_memory import DocumentMemory
from hybridagi.core.datatypes import Document, DocumentList
from .falkordb_memory import FalkorDBMemory

class FalkorDBDocumentMemory(FalkorDBMemory, DocumentMemory):
    """
    A class used to manage and store documents using FalkorDB.

    This class extends FalkorDBMemory and implements the DocumentMemory interface,
    providing a robust solution for storing and managing documents in a graph database.
    It allows for efficient storage, retrieval, and manipulation of documents using
    FalkorDB's graph capabilities.

    Key features:
    1. Document management: Store and retrieve documents with their properties.
    2. Efficient querying: Utilize FalkorDB's graph querying capabilities for fast data retrieval.
    3. Vector embeddings: Support for storing and querying vector embeddings of documents.
    4. CRUD operations: Implement create, read, update, and delete operations for documents.

    This implementation provides a scalable and flexible solution for document-based
    knowledge representation in AI and machine learning applications.
    """
    def __init__(
        self, 
        index_name: str, 
        graph_index: str = "document_memory", 
        wipe_on_start: bool = True, 
        *args, 
        **kwargs
        ):
        super().__init__(
            index_name=index_name, 
            graph_index=graph_index, 
            wipe_on_start=wipe_on_start, 
            *args, 
            **kwargs
        )

    def exist(self, doc_id) -> bool:
        return self.exists(str(doc_id), label="Document")

    def update(self, doc_or_docs: Union[Document, DocumentList]) -> None:
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
        ids = [str(id_or_ids)] if isinstance(id_or_ids, (UUID, str)) else [str(id) for id in id_or_ids]
        for id in ids:
            self.hybridstore.query(
                "MATCH (d:Document {id: $id}) DETACH DELETE d",
                params={"id": id}
            )

    def get(self, id_or_ids: Union[UUID, str, List[Union[UUID, str]]]) -> DocumentList:
        ids = [str(id_or_ids)] if isinstance(id_or_ids, (UUID, str)) else [str(id) for id in id_or_ids]
        result = self.hybridstore.query(
            "MATCH (d:Document) WHERE d.id IN $ids "
            "RETURN d.id, d.text, d.parent_id, d.vector",
            params={"ids": ids}
        )
        documents = DocumentList()
        for row in result.result_set:
            doc = Document(
                id=UUID(row[0]),
                text=row[1],
                parent_id=UUID(row[2]) if row[2] else None,
                vector=row[3]
            )
            documents.docs.append(doc)
        return documents

    def get_parents(self, id_or_ids: Union[UUID, str, List[Union[UUID, str]]]) -> DocumentList:
        ids = [str(id_or_ids)] if isinstance(id_or_ids, (UUID, str)) else [str(id) for id in id_or_ids]
        result = self.hybridstore.query(
            "MATCH (d:Document)-[:PART_OF]->(p:Document) WHERE d.id IN $ids "
            "RETURN p.id, p.text, p.parent_id, p.vector",
            params={"ids": ids}
        )
        documents = DocumentList()
        for row in result.result_set:
            doc = Document(
                id=UUID(row[0]),
                text=row[1],
                parent_id=UUID(row[2]) if row[2] else None,
                vector=row[3]
            )
            documents.docs.append(doc)
        return documents

    def clear(self):
        self.hybridstore.query("MATCH (n:Document) DETACH DELETE n")
