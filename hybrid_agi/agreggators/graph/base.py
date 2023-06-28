"""The base graph aggregator. Copyright (C) 2023 SynaLinks. License: GPL-3.0"""

import abc
import redis
from redisgraph import Graph
from typing import List, Optional
from pydantic import BaseModel, Extra

from hybrid_agi.hybridstores.redisgraph import RedisGraphHybridStore

class BaseGraphAgreggator(BaseModel):
    """Base class for knowledge graph assembler"""
    hybridstore: RedisGraphHybridStore
    
    @abc.abstractmethod
    def agreggate(self, data:List[Graph], metadata:Optional[List[dict]]) -> Graph:
        pass