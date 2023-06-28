"""The summary extractor. Copyright (C) 2023 SynaLinks. License: GPL-3.0"""

from typing import Optional
from pydantic import BaseModel, Extra
from langchain.base_language import BaseLanguageModel
from langchain.chains.llm import LLMChain

from hybrid_agi.hybridstores.redisgraph import RedisGraphHybridStore
from hybrid_agi.extractors.summary.prompt import SUMMARY_EXTRACTION_PROMPT

class SummaryExtractor(BaseModel):
    hybridstore: RedisGraphHybridStore
    llm: BaseLanguageModel
    verbose: bool = True

    class Config:
        """Configuration for this pydantic object."""
        extra = Extra.forbid
        arbitrary_types_allowed = True

    def from_text(self, text:str, metadata:Optional[dict]=None) -> str:
        """Create summary from text"""
        chain = LLMChain(llm=self.llm, prompt=SUMMARY_EXTRACTION_PROMPT, verbose=self.verbose)
        summary = chain.predict(input=text)
        key = ""
        if metadata is not None:
            ids = self.hybridstore.add_texts([summary], metadatas=[metadata])
        else:
            ids = self.hybridstore.add_texts([summary])
        key = ids[0]
        if key != "":
            self.hybridstore.metagraph.query('MERGE (:Summary {name:"'+key+'"})')
        return key

