from typing import Union, List, Dict, Optional
from uuid import UUID
from collections import OrderedDict
from hybridagi.memory.document_memory import DocumentMemory
from hybridagi.core.datatypes import Document, DocumentList

class LocalDocumentMemory(DocumentMemory):
    """
    A class used to store documents locally.
    It inherits from the DocumentMemory class and provides methods to update, remove, and retrieve documents.
    """
    index_name: str
    _nodes: Optional[Dict[str, Document]] = {}
    _edges: Optional[Dict[str, Dict[str, str]]] = {}
    
    _embeddings: Optional[Dict[str, List[float]]] = OrderedDict()
    
    def __init__(self, index_name: str, wipe_on_start: bool=True):
        """
        Initialize the local document memory.

        Parameters:
            wipe_on_start (bool): Whether to clear the memory when the object is initialized.
        """
        self.index_name = index_name
        if wipe_on_start:
            self.clear()
    
    def update(self, doc_or_docs: Union[Document, DocumentList]) -> None:
        """
        Update the local document memory with new documents.

        Parameters:
            doc_or_docs (Union[Document, DocumentList]): A single document or a list of documents to be added to the memory.

        Raises:
            ValueError: If the input is not a Document or DocumentList.
        """
        if not isinstance(doc_or_docs, Document) and not isinstance(doc_or_docs, DocumentList):
            raise ValueError("Invalid datatype provided must be Document or DocumentList")
        if isinstance(doc_or_docs, Document):
            documents = DocumentList()
            documents.docs = [doc_or_docs]
        else:
            documents = doc_or_docs
        for doc in documents.docs:
            self._nodes[str(doc.id)] = doc
            self._embeddings[str(doc.id)] = doc.vector
            if doc.parent_id:
                if str(doc.parent_id) not in self._edges:
                    self._edges[str(doc.parent_id)] = {}
                self._edges[str(doc.parent_id)][str(doc.id)] = "CONTAINS"
            if doc.vector:
                self._embeddings[str(doc.id)] = doc.vector
            
    def remove(self, id_or_ids: Union[Union[UUID, str], List[Union[UUID, str]]]) -> None:
        """
        Remove documents from the local document memory.

        Parameters:
            id_or_ids (Union[Union[UUID, str], List[Union[UUID, str]]]): A single document id or a list of document ids to be removed from the memory.
        """
        if not isinstance(id_or_ids, list):
            document_ids = [id_or_ids]
        else:
            document_ids = id_or_ids
        for doc_id in document_ids:
            if str(doc_id) in self._nodes:
                del self._nodes[str(doc_id)]
            if str(doc_id) in self._embeddings:
                del self._embeddings[str(doc_id)]
            # TODO remove edges cleanly
                
    def get(self, id_or_ids: Union[Union[UUID, str], List[Union[UUID, str]]]) -> DocumentList:
        """
        Retrieve documents from the local document memory.

        Parameters:
            id_or_ids (Union[Union[UUID, str], List[Union[UUID, str]]]): A single document id or a list of document ids to be retrieved from the memory.

        Returns:
            DocumentList: A list of documents that match the input ids.

        Raises:
            ValueError: If the input ids are not valid.
        """
        if not isinstance(id_or_ids, list):
            document_ids = [id_or_ids]
        else:
            document_ids = id_or_ids
        result = DocumentList()
        for doc_id in document_ids:
            if str(doc_id) in self._nodes:
                doc = self._nodes[str(doc_id)]
                result.docs.append(doc)
        return result
    
    def get_parent(self, id_or_ids: Union[Union[UUID, str], List[Union[UUID, str]]]) -> DocumentList:
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
            document_ids = [id_or_ids]
        result = DocumentList()
        for doc_id in document_ids:
            if str(doc_id) in self._nodes:
                parent_id = self._nodes[str(doc_id)]
                if str(parent_id) in self._nodes:
                    doc = self._nodes[str(parent_id)]
                    result.docs.append(doc)
        return result
    
    def clear(self):
        """
        Clear the local document memory.
        This method removes all documents, edges, and embeddings from the memory.
        """
        self._nodes = {}
        self._edges = {}
        self._embeddings = {}
    
    def visualize(self, notebook=False):
        """
        Visualize the local document memory as a network graph.

        Parameters:
            notebook (bool): Whether to display the graph in a Jupyter notebook or not.
        """
        #TODO
        # from pyvis.network import Network
        # net = Network(notebook=notebook, directed=True)
        # for node_name, node in self._nodes.items():
        #     root_color = "red"
        #     child_color = "orange"
        #     color = child_color if node.parent_id else root_color
        #     net.add_node(node_name, title=node.text, color=color)
        # # for source_id in self._edges:
        # #     for target_id in self._edges:
                
        # #         net.add_edge(source_id, target_id)
        # #TODO
        # net.toggle_physics(True)
        # net.show('{index_name}_document_memory.html', notebook=False)
    
        