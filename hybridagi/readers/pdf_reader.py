import pymupdf
from hybridagi.core.datatypes import Document, DocumentList
from .document_reader import DocumentReader
 
class PDFReader(DocumentReader):
    
    def read(self, filepath: str) -> DocumentList:
        result = DocumentList()
        pdf_document = pymupdf.open(filepath)
        for page_nb, page in enumerate(pdf_document): # iterate over the document pages
            text = page.get_text()
            result.docs.append(
                Document(
                    text=text,
                    metadata={"filepath": filepath, "page": page_nb},
                )
            )
        return result