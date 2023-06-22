"""The base class for graph loaders. Copyright (C) 2023 SynaLinks. License: GPLv3"""

import abc
from pydantic import BaseModel
from redisgraph import Graph

class BaseGraphLoader(BaseModel):
    """Base class to load data into the graph database"""
    client: redis.Redis
    filepath: str
    graph_key: str = "graph"

    @abc.abstractmethod
    def load() -> Graph:
        """Method to load file"""
        pass