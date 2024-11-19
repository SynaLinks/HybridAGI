import dspy
from typing import List, Optional, Union
from hybridagi.core.datatypes import Document, DocumentList, GraphProgramList
from hybridagi.modules.extractors.document_extractor import DocumentExtractor
from hybridagi.modules.agents.tools import Tool
from tqdm import tqdm

class PlanExtractorSignature(dspy.Signature):
    """You will be given a `document`, `routines` and `tools` field, your task is to infer the `plan` field
To infer the `plan` field, ensure to follow the following instructions:
- ONLY use the provided list of tools
- Ensure that you plan is coherent
- Always minimize the number of steps
- Write down EXPLICITLY the decision making steps if any and what step should follow each of the outcome
- You don't have to use all the tools provided, just the ones needed
"""
    document: str = dspy.InputField(desc="The input document")
    tools: str = dspy.InputField(desc="The available tools")
    routines: str = dspy.InputField(desc="The sub-routines that you can use")
    plan: str = dspy.OutputField(desc="The output plan")

class PlanExtractor(DocumentExtractor):
    
    def __init__(
            self,
            lm: Optional[dspy.LM] = None,
            tools: List[Tool] = [],
            programs: GraphProgramList = GraphProgramList(),
        ):
        self.predict = dspy.Predict(PlanExtractorSignature)
        tools_instructions = []
        for tool in tools:
            tools_instructions.append(f"- [{tool.name}]: {tool.description}")
        if tools_instructions:
            self.tools_instructions = "\n".join(tools_instructions)
        else:
            self.tools_instructions = "No tools provided"
        programs_instructions = []
        for program in programs.progs:
            programs_instructions.append(f"- [{program.name}]: {program.description}")
        if programs_instructions:
            self.programs_instructions = "\n".join(tools_instructions)
        else:
            self.programs_instructions = "No sub-routines provided"
        
    def forward(self, doc_or_docs: Union[Document, DocumentList]) -> DocumentList:
        if not isinstance(doc_or_docs, (Document, DocumentList)):
            raise ValueError(f"{type(self).__name__} input must be a Document or DocumentList")
        if isinstance(doc_or_docs, Document):
            documents = DocumentList()
            documents.docs = [doc_or_docs]
        else:
            documents = doc_or_docs
        result = DocumentList()
        for doc in tqdm(documents):
            with dspy.context(lm=self.lm if self.lm is not None else dspy.settings.lm):
                pred = self.predict(
                    document = doc,
                    tools = self.tools_instructions,
                    routines = self.programs_instructions,
                )
            result.docs.append(Document(text=pred.plan))
        return result