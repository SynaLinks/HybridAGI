from .base import BaseTraceMemory
from typing import Optional, Callable, Any
from pydantic.v1 import Extra
from langchain.schema.embeddings import Embeddings
from .base import _default_norm

class TraceMemory(BaseTraceMemory):

    class Config:
        """Configuration for this pydantic object."""
        extra = Extra.forbid
        arbitrary_types_allowed = True

    def __init__(
            self,
            index_name: str,
            redis_url: str,
            embeddings: Embeddings,
            embeddings_dim: int,
            normalize: Optional[Callable[[Any], Any]] = _default_norm,
            verbose: bool = True):
        super().__init__(
            index_name = index_name,
            redis_url = redis_url,
            embeddings = embeddings,
            embeddings_dim = embeddings_dim,
            normalize = normalize,
            verbose = verbose,
        )

    