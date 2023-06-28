"""The base class for graph loaders. Copyright (C) 2023 SynaLinks. License: GPL-3.0"""

import abc
import redis
from pydantic import BaseModel, Extra
from redisgraph import Graph

class BaseGraphLoader(BaseModel):
    """Base class to load data into the graph database"""
    client: redis.Redis
    graph_key: str = "graph"

    class Config:
        """Configuration for this pydantic object."""
        extra = Extra.forbid
        arbitrary_types_allowed = True

    @abc.abstractmethod
    def load(self, filepath: str, index: str = "") -> Graph:
        """Method to load file"""
        pass