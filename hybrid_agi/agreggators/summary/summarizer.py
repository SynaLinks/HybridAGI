"""The summarizer summary aggregator. Copyright (C) 2023 SynaLinks. License: GPL-3.0"""

import abc
import redis
from redisgraph import Graph
from typing import List, Optional
from pydantic import BaseModel, Extra

from hybrid_agi.hybridstores.redisgraph import RedisGraphHybridStore
from langchain.base_language import BaseLanguageModel
from hybrid_agi.aggregators.summary.base import BaseSummaryAgreggator

class SummarizerAgreggator(BaseSummaryAgreggator):
    """Base class for knowledge graph assembler"""
    hybridstore: RedisGraphHybridStore
    llm: BaseLanguageModel
    
    @abc.abstractmethod
    def agreggate(self, data:List[Node], metadata:Optional[List[dict]]) -> Node:
        raise NotImplementedError("Not Implemented yet.")