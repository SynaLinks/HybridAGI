import dspy
import re
from tqdm import tqdm
from abc import abstractmethod
from typing import Union, Optional
from hybridagi.modules.extractors import FactExtractor
from hybridagi.core.datatypes import Document, DocumentList, Fact, Relationship, Entity, FactList, GraphSchema

class FactExtractorSignature(dspy.Signature):
    """Given the fields `document`, produce the fields `triplets`.
    To infer the field `triplets`, please use the following syntax:
    
    (:SubjectLabel1 {name:"Subject Name1"})-[:PREDICATE1]->(:ObjectLabel1 {name:"Object Name1"}),
    (:SubjectLabel2 {name:"Subject Name2"})-[:PREDICATE2]->(:ObjectLabel2 {name:"Object Name2"}),
    ... N times
    
    Ensure to always use only the name property and give short labels to nodes.
    """
    document: str = dspy.InputField(desc="The input document")
    triplets: str = dspy.OutputField(desc="The comma separated triplets extracted from the document")
    
class LLMFactExtractor(FactExtractor):
    
    def __init__(
            self,
            schema: Optional[GraphSchema] = None,
            lm: Optional[dspy.LM] = None,
        ):
        self.lm = lm
        self.extraction = dspy.Predict(FactExtractorSignature)
    
    def forward(self, doc_or_docs: Union[Document, DocumentList])-> FactList:
        if not isinstance(doc_or_docs, Document) and not isinstance(doc_or_docs, DocumentList):
            raise ValueError(f"{type(self).__name__} input must be a Document or DocumentList")
        if isinstance(doc_or_docs, Document):
            documents = DocumentList()
            documents.docs = [doc_or_docs]
        else:
            documents = doc_or_docs
        result = FactList()
        for doc in tqdm(documents.docs):
            with dspy.context(lm=self.lm if self.lm is not None else dspy.settings.lm):
                pred = self.extraction(
                    document = doc.text,
                )
            result.from_cypher(pred.triplets, doc.metadata)
        return result