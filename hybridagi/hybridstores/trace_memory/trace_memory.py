from collections import deque
from .base import BaseTraceMemory
from typing import Optional, Callable, Any
from langchain.schema.embeddings import Embeddings
from .base import _default_norm

START_PROGRAM_DESCRIPTION = \
"""Start Program: {program_name}
Program Purpose: {purpose}"""

END_PROGRAM_DESCRIPTION = \
"""End Program: {program_name}"""

ACTION_DESCRIPTION = \
"""Action Purpose: {purpose}
Action: {tool_name}
Action Input: {tool_input}
Action Observation: {tool_observation}"""

DECISION_DESCRIPTION = \
"""Decision Purpose: {purpose}
Decision: {question}
Decision Answer: {decision}"""

class TraceMemory(BaseTraceMemory):
    """The trace memory"""
    commit_index_trace: deque = deque()
    last_decision_index: str = ""

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