## The base aggregator.
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