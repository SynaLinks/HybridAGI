import dspy
from tqdm import tqdm
from typing import Union, Optional
from hybridagi.modules.extractors import DocumentExtractor
from hybridagi.core.datatypes import Document, DocumentList

class ClaimExtractorSignature(dspy.Signature):
    document: str = dspy.InputField(desc="The input document")
    claims: str = dspy.OutputField(desc="The comma separated claims (factual assertions) contained in the document")

class LLMClaimExtractor(DocumentExtractor):
    
    def __init__(
            self,
            lm: Optional[dspy.LM] = None,
        ):
        self.lm = lm
        self.extraction = dspy.Predict(ClaimExtractorSignature)
    
    def forward(self, doc_or_docs: Union[Document, DocumentList])-> DocumentList:
        if not isinstance(doc_or_docs, Document) and not isinstance(doc_or_docs, DocumentList):
            raise ValueError(f"{type(self).__name__} input must be a Document or DocumentList")
        if isinstance(doc_or_docs, Document):
            documents = DocumentList()
            documents.docs = [doc_or_docs]
        else:
            documents = doc_or_docs
        result = DocumentList()
        for doc in tqdm(documents.docs):
            with dspy.context(lm=self.lm if self.lm is not None else dspy.settings.lm):
                pred = self.extraction(
                    document = doc.text,
                )
            claims = pred.claims.split(",")
            for claim in claims:
                result.docs.append(Document(
                    text = claim.strip(),
                    parent_id = doc.id,
                    metadata = doc.metadata,
                ))
        return result