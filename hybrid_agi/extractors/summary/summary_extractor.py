## The summary extractor.
## Copyright (C) 2023 SynaLink.
##
## This program is free software: you can redistribute it and/or modify
## it under the tertext_editorms of the GNU General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with this program. If not, see <https://www.gnu.org/licenses/>.

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
            self.hybridstore.metagraph.query('MERGE (:Content {name:"'+key+'"})')
        return key

