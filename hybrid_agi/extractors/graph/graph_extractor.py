## The graph extractor.
## Copyright (C) 2023 SynaLinks.
##
## This program is free software: you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
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

import uuid
from colorama import Fore, Style
from typing import Optional, Type
from pydantic import BaseModel, Extra
from redisgraph import Graph
from langchain.base_language import BaseLanguageModel
from langchain.prompts.prompt import PromptTemplate
from langchain.chains.llm import LLMChain

from hybrid_agi.hybridstores.redisgraph import RedisGraphHybridStore
from hybrid_agi.extractors.graph.prompt import (
    GRAPH_EXTRACTION_THINKING_PROMPT,
    GRAPH_EXTRACTION_PROMPT
)

from hybrid_agi.parsers.cypher import CypherOutputParser

class GraphExtractor(BaseModel):
    """Functionality to extract graph."""
    hybridstore: RedisGraphHybridStore
    llm: BaseLanguageModel
    max_extraction_attemps: int = 3,
    verbose: bool = True

    class Config:
        """Configuration for this pydantic object."""
        extra = Extra.forbid
        arbitrary_types_allowed = True

    def from_text(self, text:str) -> Optional[Graph]:
        """Create graph from text."""
        thinking_chain = LLMChain(llm=self.llm, prompt=GRAPH_EXTRACTION_THINKING_PROMPT, verbose=self.verbose)
        thoughts = thinking_chain.predict(input=text)
        graph = self.extract_graph(text, GRAPH_EXTRACTION_PROMPT.partial(thoughts=thoughts))
        if graph is not None:
            self.hybridstore.metagraph.query('MERGE (:Plan {name:"'+graph.name+'"})')
        return graph

    def extract_graph(self, input_data:str, prompt) -> Optional[Graph]:
        if self.llm is None:
            raise ValueError("LLM should not be None")
        cypher_query = ""
        graph = None
        # First we extract the graph representation from the text.
        extraction_chain = LLMChain(llm=self.llm, prompt=prompt, verbose=self.verbose)
        cypher_query = extraction_chain.predict(input=input_data)
        parser = CypherOutputParser()
        cypher_query = parser.parse(cypher_query)
        # Then we create the RedisGraph client.
        graph = Graph(
            self.hybridstore.redis_key(
                self.hybridstore.graph_key
                ),
            self.hybridstore.client
        )
        # To then try to populate the graph with the extracted data.
        extraction_attemps = 0
        while extraction_attemps < self.max_extraction_attemps:
            try:
                graph.query(cypher_query)
                return graph
            except Exception as err:
                print(f"{Fore.RED}[!] Failed to extract graph: {str(err)}{Style.RESET_ALL}")
                print(f"{Fore.RED}[!] "+cypher_query+f"{Style.RESET_ALL}")
                cypher_query = extraction_chain.predict(input=input_data)
                parser = CypherOutputParser()
                cypher_query = parser.parse(cypher_query)
        graph.delete()
        if self.verbose:
            print(f"{Fore.YELLOW}{cypher_query}{Style.RESET_ALL}")
        return None