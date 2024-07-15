import hybridagi.core.datatypes as dt

class DocumentEmbedder(dspy.Module):
    
    def __init__(
            self,
            embeddings: Embeddings,
        ):
        pass#TODO
    
    def forward(self, doc_or_docs: Union[dt.Document, dt.DocumentList]) -> dt.DocumentList:
        pass#TODO