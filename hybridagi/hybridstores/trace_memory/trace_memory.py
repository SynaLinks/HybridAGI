from .base import BaseTraceMemory
from typing import Optional, Callable, Any
from langchain.schema.embeddings import Embeddings
from .base import _default_norm
from pydantic.v1 import Extra

class TraceMemory(BaseTraceMemory):

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

    