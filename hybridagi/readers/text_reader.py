from hybridagi.core.datatypes import Document, DocumentList
from .document_reader import DocumentReader

class TextReader(DocumentReader):
    
    def read(self, filepath: str) -> DocumentList:
        result = DocumentList()
        with open(filepath, "r") as f:
            document = Document(text=f.read(), metadata={"filepath": filepath})
        result.docs.append(document)
        return result