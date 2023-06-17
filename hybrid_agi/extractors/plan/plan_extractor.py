## The plan extractor.
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

import redis
from typing import Optional
from pydantic import BaseModel
from redisgraph import Graph
from hybrid_agi.extractors.graph.graph_extractor import GraphExtractor

from hybrid_agi.extractors.plan.prompt import (
    PLAN_EXTRACTION_THINKING_PROMPT,
    PLAN_EXTRACTION_PROMPT,
    PLAN_EXAMPLE,
    PLAN_EXAMPLE_SMALL
)

class PlanExtractor(GraphExtractor):
    """Functionality to extract plan."""

    def from_text(self, text: str) -> Optional[Graph]:
        """Create plan from text."""
        thinking_chain = LLMChain(llm=self.llm, prompt=PLAN_EXTRACTION_THINKING_PROMPT, verbose=self.verbose)
        thoughts = thinking_chain.predict(input=text)
        plan = self.extract_graph(text, PLAN_EXTRACTION_PROMPT.partial(thoughts=thoughts, example=PLAN_EXAMPLE_SMALL))
        if plan is not None:
            self.hybridstore.metagraph.query('MERGE (:Plan {name:"'+plan.name+'"})')
        return plan