from tqdm import tqdm
from typing import Union
from hybridagi.modules.splitters import DocumentSplitter
from hybridagi.core.datatypes import Document, DocumentList
from docling_core.types.doc.document import DoclingDocument
from docling_core.transforms.chunker.hierarchical_chunker import HierarchicalChunker

class DoclingHierarchicalChunker(DocumentSplitter):
    """A document splitter that uses Docling's hierarchical chunking capabilities.
    
    This class implements document splitting using Docling's HierarchicalChunker to break down
    documents into meaningful chunks while preserving their hierarchical structure. It works with
    both individual documents and document lists.

    Inherits From:
        DocumentSplitter: Base class for document splitting operations

    Attributes:
        doclingdoc (DoclingDocument): A Docling document object. It may have been already processed or
        read from storage.
    """
    def __init__(
            self,
            doclingdoc: DoclingDocument
        ):
        self.doclingdoc = doclingdoc
    
    def forward(self, doc_or_docs: Union[Document, DocumentList]) -> DocumentList:
        """Performs hierarchical chunking on the input document(s).

        This method processes either a single HybridAGI Document or a DocumentList using Docling's
        HierarchicalChunker. It preserves document metadata and maintains parent-child relationships
        between documents and their chunks.

        Args:
            doc_or_docs (Union[Document, DocumentList]): Either a single HybridAGI Document object or a 
                DocumentList containing multiple documents to be chunked

        Returns:
            DocumentList: A HybridAGI DocumentList object, where each document represents a chunk
                from the original document(s). Each chunk maintains metadata from its parent
                document and includes a reference to its parent's ID.

        Raises:
            ValueError: If the input is neither a HybridAGI Document nor a DocumentList

        Example:
            ```python
            document_pipeline = Pipeline()
            document_pipeline.add("chunk_documents", DoclingHierarchicalChunker(doclingdoc=dt)) # dt is a DoclingDocument
            document_pipeline.add("embed_chunks", DocumentEmbedder(embeddings=embeddings))
            
            presentation_chunks = document_pipeline(presentation_doc)
            presentation_memory = LocalDocumentMemory(index_name="company_presentation")
            presentation_memory.update(presentation_doc)
            presentation_memory.update(presentation_chunks)
            ```
        """
        if not isinstance(doc_or_docs, Document) and not isinstance(doc_or_docs, DocumentList):
            raise ValueError("Invalid datatype provided must be Document or DocumentList")
        if isinstance(doc_or_docs, Document):
            documents = DocumentList()
            documents.docs = [doc_or_docs]
        else:
            documents = doc_or_docs
        result = DocumentList()
        for doc in tqdm(documents.docs):
            fullchunks = list(HierarchicalChunker().chunk(self.doclingdoc))
            for chunk in fullchunks:
                new_doc = Document(
                    text=chunk.text,
                    metadata=doc.metadata,
                    parent_id=doc.id,
                )
                if result.docs is not None:
                    result.docs.append(new_doc)
        return result