import abc
import numpy as np
from typing import Union, List

class BaseEmbeddings():
    
    def __init__(self, dim: int):
        self.dim = dim

    @abc.abstractmethod
    def embed_text(self, query_or_queries: Union[str, List[str]]) -> np._typing.NDArray:
        pass
    
    @abc.abstractmethod
    def embed_image(self, image_or_images: Union[np._typing.NDArray, List[np._typing.NDArray]]) -> np._typing.NDArray:
        pass