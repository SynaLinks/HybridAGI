"""The embeddings. Copyright (C) 2024 SynaLinks. License: GPL-3.0"""

from abc import ABC, abstractmethod
import numpy as np
from typing import Union, List

class Embeddings(ABC):
    
    def __init__(self, dim: int):
        self.dim = dim

    @abstractmethod
    def embed_text(self, query_or_queries: Union[str, List[str]]) -> np._typing.NDArray:
        raise NotImplementedError(
            f"Embeddings {type(self).__name__} is missing the required 'embed_text' method."
        )
    
    @abstractmethod
    def embed_image(self, image_or_images: Union[np._typing.NDArray, List[np._typing.NDArray]]) -> np._typing.NDArray:
        raise NotImplementedError(
            f"Embeddings {type(self).__name__} is missing the required 'embed_image' method."
        )