from pypdf import PdfReader
from hybridagi.core.datatypes import Document, DocumentList
from .document_reader import DocumentReader
 
class PDFReader(DocumentReader):
    
    def read(self, filepath: str) -> DocumentList:
        result = DocumentList()
        reader = PdfReader(filepath)
        for page_nb, page in enumerate(reader.pages): # iterate over the document pages
            text = page.extract_text().replace("\n", " ")
            result.docs.append(
                Document(
                    text=text,
                    metadata={"filepath": filepath, "page": page_nb},
                )
            )
        return result