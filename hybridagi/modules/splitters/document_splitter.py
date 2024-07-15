import hybridagi.core.datatypes as dt

class DocumentSplitter(dspy.Module):
    
    def __init__(
            self,
            method: str = "word",
            chunk_size: int = 256,
            chunk_overlap: int = 0,
            split_word = "\n\n",
        ):
        pass#TODO
    
    def forward(self, doc_or_docs: Union[dt.Document, dt.DocumentList]) -> dt.DocumentList:
        pass#TODO