import dspy
from tqdm import tqdm
from typing import Union
from hybridagi.embeddings.embeddings import Embeddings
from hybridagi.core.datatypes import Document, DocumentList

class DocumentEmbedder(dspy.Module):
    """
    A class used to embed documents using a pre-trained embedding model.

    Attributes:
        embeddings (Embeddings): The pre-trained embedding model to be used for embedding documents.
    """    
    def __init__(
            self,
            embeddings: Embeddings,
        ):
        """
        Initialize the DocumentEmbedder.

        Parameters:
            embeddings (Embeddings): The pre-trained embedding model to be used for embedding documents.
        """
        self.embeddings = embeddings 
    
    def forward(self, doc_or_docs: Union[Document, DocumentList]) -> DocumentList:
        """
        Embed documents using the pre-trained embedding model.

        Parameters:
            doc_or_docs (Union[Document, DocumentList]): A single document or a list of documents to be embedded.

        Returns:
            DocumentList: A list of documents with their corresponding embeddings.

        Raises:
            ValueError: If the input is not a Document or DocumentList.
        """
        if not isinstance(doc_or_docs, Document) and not isinstance(doc_or_docs, DocumentList):
            raise ValueError(f"{type(self).__name__} input must be a Document or DocumentList")
        if isinstance(doc_or_docs, Document):
            documents = DocumentList()
            documents.docs = [doc_or_docs]
        else:
            documents = doc_or_docs
        for doc in tqdm(documents.docs):
            doc.vector = self.embeddings.embed_text(doc.text)
        return documents