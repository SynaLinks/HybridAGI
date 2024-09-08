from typing import Union, List, Dict, Optional
from uuid import UUID
from collections import OrderedDict
from hybridagi.memory.document_memory import DocumentMemory
from hybridagi.core.datatypes import Document, DocumentList
import networkx as nx

from .local_memory import LocalMemory


class LocalDocumentMemory(LocalMemory, DocumentMemory):
    """
    A class used to manage and store documents locally.

    Attributes:
        index_name (str): The name of the index used for document storage.
        wipe_on_start (bool):  Whether to clear the memory when the object is initialized.
        _documents (Optional[Dict[str, Document]]): A dictionary to store documents.
            The keys are document IDs and the values are Document objects.
        _embeddings (Optional[Dict[str, List[float]]]): An ordered dictionary to store document embeddings.
            The keys are document IDs and the values are lists of floats representing the embeddings.
    """
    index_name: str
    wipe_on_start: bool
    _documents: Optional[Dict[str, Document]] = {}
    _embeddings: Optional[Dict[str, List[float]]] = OrderedDict()
    _graph = nx.DiGraph()
    
    def __init__(
            self,
            index_name: str,
            wipe_on_start: bool = True,
        ):
        """
        Initialize the local document memory.

        Parameters:
            wipe_on_start (bool): Whether to clear the memory when the object is initialized.
        """
        self.index_name = index_name
        self.wipe_on_start = wipe_on_start
        if wipe_on_start:
            self.clear()
            
    def exist(self, doc_id) -> bool:
        return doc_id in self._documents
    
    def update(self, doc_or_docs: Union[Document, DocumentList]) -> None:
        """
        Update the local document memory with new documents.

        Parameters:
            doc_or_docs (Union[Document, DocumentList]): A single document or a list of documents to be added to the memory.

        Raises:
            ValueError: If the input is neither a Document or DocumentList.
        
        Note:
            - If a document with the given ID already exists, it will be updated.
            - If a document with the given ID doesn't exist, a new one will be created.
            - For documents with a parent_id, a PART_OF relationship is created or updated.
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
            if not self.exist(doc_id):
                parent_id = str(doc.parent_id)
                if doc.parent_id is not None:
                    parent_id = str(doc.parent_id)
                    self._graph.add_node(doc_id, color="orange", title=doc.text)
                    if parent_id in self._documents:
                        self._graph.add_edge(doc_id, parent_id, label="PART_OF")
                else:
                    self._graph.add_node(doc_id, color="red", title=doc.text)
            self._documents[doc_id] = doc
            if doc.vector is not None:
                self._embeddings[doc_id] = doc.vector
            
    def remove(self, id_or_ids: Union[UUID, str, List[Union[UUID, str]]]) -> None:
        """
        Remove documents from the local document memory.

        Parameters:
            id_or_ids (Union[Union[UUID, str], List[Union[UUID, str]]]): A single document id or a list of document ids to be removed from the memory.
        """
        if not isinstance(id_or_ids, list):
            documents_ids = [id_or_ids]
        else:
            documents_ids = id_or_ids
        for doc_id in documents_ids:
            doc_id = str(doc_id)
            if doc_id in self._documents:
                del self._documents[doc_id]
            if doc_id in self._embeddings:
                del self._embeddings[doc_id]
                
    def get(self, id_or_ids: Union[UUID, str, List[Union[UUID, str]]]) -> DocumentList:
        """
        Retrieve documents from the local document memory.

        Parameters:
            id_or_ids (Union[Union[UUID, str], List[Union[UUID, str]]]): A single document id or a list of document ids to be retrieved from the memory.

        Returns:
            DocumentList: A list of documents that match the input ids.
        """
        if not isinstance(id_or_ids, list):
            documents_ids = [id_or_ids]
        else:
            documents_ids = id_or_ids
        result = DocumentList()
        for doc_id in documents_ids:
            if str(doc_id) in self._documents:
                doc = self._documents[str(doc_id)]
                result.docs.append(doc)
        return result
    
    def get_parents(self, id_or_ids: Union[UUID, str, List[Union[UUID, str]]]) -> DocumentList:
        """
        Retrieve the parent documents of the input documents from the local document memory.

        Parameters:
            id_or_ids (Union[Union[UUID, str], List[Union[UUID, str]]]): A single document id or a list of document ids whose parent documents are to be retrieved from the memory.

        Returns:
            DocumentList: A list of parent documents that match the input ids.

        Raises:
            ValueError: If the input ids are not valid.
        """
        if not isinstance(id_or_ids, list):
            documents_ids = [id_or_ids]
        result = DocumentList()
        for doc_id in documents_ids:
            doc_id = str(doc_id)
            if doc_id in self._documents:
                parent_id = str(self._documents[doc_id].parent_id)
                if parent_id in self._documents:
                    doc = self._documents[parent_id]
                    result.docs.append(doc)
        return result
    
    def clear(self):
        """
        Clear the local document memory.
        This method removes all documents, graph, and embeddings from the memory.
        """
        self._documents = {}
        self._embeddings = {}
        self._graph = nx.DiGraph()
