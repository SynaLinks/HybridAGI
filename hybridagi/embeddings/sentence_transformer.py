"""The sentence embeddings. Copyright (C) 2024 SynaLinks. License: GPL-3.0"""
# Modified from dspy vectorizer

import numpy as np
from typing import Union, List
from hybridagi.embeddings.embeddings import Embeddings

class SentenceTransformerEmbeddings(Embeddings):

    def __init__(
            self,
            model_name_or_path: str,
            dim: int,
            max_gpu_devices: int = 1,
            batch_size: int = 256,
            max_seq_length: int = 256,
            normalize_embeddings: bool = True,
        ):
        super().__init__(dim=dim)
        self.model_name_or_path = model_name_or_path
        self.max_gpu_devices = max_gpu_devices
        self.batch_size = batch_size
        self.max_seq_length= max_seq_length
        self.normalize_embeddings = normalize_embeddings
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError:
            raise ImportError(
                "You need to install sentence_transformers library to use pretrained embeddings. "
                "Please run `pip install sentence-transformers`",
            )
        try:
            from dsp.utils.ann_utils import determine_devices
        except ImportError:
            raise ImportError(
                "You need to install faiss library to use pretrained embeddings. "
                "Please run `pip install faiss-gpu` or `pip install faiss-cpu`",
            )
        self.num_devices, self.is_gpu = determine_devices(self.max_gpu_devices)
        self.proxy_device = 'cuda' if self.is_gpu else 'cpu'

        self.model = SentenceTransformer(self.model_name_or_path, device=self.proxy_device)
        self.model.max_seq_length = self.max_seq_length

    def embed_text(self, query_or_queries: Union[str, List[str]]) -> np._typing.NDArray:
        if isinstance(query_or_queries, str) and query_or_queries == "":
            raise ValueError("Input cannot be an empty string.")
        
        text_to_vectorize = [query_or_queries] if not isinstance(query_or_queries, list) else query_or_queries

        if self.is_gpu and self.num_devices > 1:
            target_devices = list(range(self.num_devices))
            pool = self.model.start_multi_process_pool(target_devices=target_devices)
            # Compute the embeddings using the multi-process pool
            emb = self.model.encode_multi_process(
                sentences=text_to_vectorize,
                pool=pool,
                batch_size=self.batch_size,
            )
            self.model.stop_multi_process_pool(pool)
            # for some reason, multi-GPU setup doesn't accept normalize_embeddings parameter
            if self.normalize_embeddings:
                emb = emb / np.linalg.norm(emb)
        else:
            emb = self.model.encode(
                sentences=text_to_vectorize,
                batch_size=self.batch_size,
                normalize_embeddings=self.normalize_embeddings,
            )
        if not isinstance(query_or_queries, list):
            return emb[0]
        else:
            return emb
    
    def embed_image(self, image_or_images: Union[np._typing.NDArray, List[np._typing.NDArray]]) -> np._typing.NDArray:
        raise NotImplementedError("SentenceTransformer does not support image embeddings")
