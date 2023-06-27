"""The plan extractor. Copyright (C) 2023 SynaLinks. License: GPLv3"""

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
        thought = thinking_chain.predict(input=text)
        plan = self.extract_graph(text, PLAN_EXTRACTION_PROMPT.partial(thought=thought, example=PLAN_EXAMPLE_SMALL))
        if plan is not None:
            self.hybridstore.metagraph.query('MERGE (:Plan {name:"'+plan.name+'"})')
        return plan