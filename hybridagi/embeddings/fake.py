import numpy as np
from typing import Union, List
from .base import BaseEmbeddings

class FakeEmbeddings(BaseEmbeddings):
    
    def __init__(
            self,
            dim: int,
            normalize_embeddings: bool = True,
        ):
        super().__init__(dim=dim)
        self.normalize_embeddings = normalize_embeddings

    def embed_text(self, query_or_queries: Union[str, List[str]]) -> np._typing.NDArray:
        if not isinstance(query_or_queries, list):
            emb = np.random.random(self.dim)
            if self.normalize_embeddings:
                return emb / np.linalg.norm(emb)
            else:
                return emb
        else:
            embeddings = []
            for _ in query_or_queries:
                emb = np.random.random(self.dim)
                if self.normalize_embeddings:
                    embeddings.append(emb / np.linalg.norm(emb))
                else:
                    embeddings.append(emb)
            return embeddings
    
    def embed_image(self, image_or_images: Union[np._typing.NDArray, List[np._typing.NDArray]]) -> np._typing.NDArray:
        if not isinstance(image_or_images, list):
            emb = np.random.random(self.dim)
            if self.normalize_embeddings:
                return emb / np.linalg.norm(emb)
            else:
                return emb
        else:
            embeddings = []
            for _ in image_or_images:
                emb = np.random.random(self.dim)
                if self.normalize_embeddings:
                    embeddings.append(emb / np.linalg.norm(emb))
                else:
                    embeddings.append(emb)
            return embeddings