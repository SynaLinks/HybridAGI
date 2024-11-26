import numpy as np
from typing import Union, List
from hybridagi.embeddings.embeddings import Embeddings

class OllamaEmbeddings(Embeddings):
    def __init__(
            self,
            model_name: str = "mxbai-embed-large:latest",
            dim: int = 1024,  # Adjust default dimension based on your model
            batch_size: int = 32,
        ):
        """Initialize the Ollama embeddings class.
        
        Args:
            model_name: Name of the Ollama model to use for embeddings
            dim: Dimension of the embedding vectors
            batch_size: Number of texts to process at once
        """
        super().__init__(dim=dim)
        self.model_name = model_name
        self.batch_size = batch_size
        
        try:
            import ollama
        except ImportError:
            raise ImportError(
                "You need to install ollama library to use Ollama embeddings. Obviously, you also need an Ollama server running."
                "Please run `pip install ollama`"
            )
        self.ollama = ollama

    def _batch_embed(self, texts: List[str]) -> np.ndarray:
        """Embed a batch of texts using Ollama.
        
        Args:
            texts: List of strings to embed
            
        Returns:
            numpy.ndarray: Array of embeddings
        """
        all_embeddings = []
        
        # Process in batches
        for i in range(0, len(texts), self.batch_size):
            batch = texts[i:i + self.batch_size]
            # Get embeddings for the entire batch at once
            response = self.ollama.embed(
                model=self.model_name,
                input=batch
            )
            # Convert the embeddings list to numpy array
            batch_embeddings = np.array(response['embeddings'], dtype=np.float32)
            all_embeddings.append(batch_embeddings)
            
        # Concatenate all batches
        return np.concatenate(all_embeddings) if len(all_embeddings) > 1 else all_embeddings[0]

    def embed_text(self, query_or_queries: Union[str, List[str]]) -> np.ndarray:
        """Embed text or list of texts using Ollama.
        
        Args:
            query_or_queries: Single string or list of strings to embed
            
        Returns:
            numpy.ndarray: Array of embeddings
            
        Raises:
            ValueError: If input is an empty string
        """
        if isinstance(query_or_queries, str):
            if query_or_queries == "":
                raise ValueError("Input cannot be an empty string.")
            
            # Single string case
            response = self.ollama.embed(
                model=self.model_name,
                input=query_or_queries
            )
            return np.array(response['embeddings'][0], dtype=np.float32)
        else:
            # List of strings case
            if not query_or_queries:  # Empty list check
                raise ValueError("Input cannot be an empty list.")
                
            return self._batch_embed(query_or_queries)
    
    def embed_image(self, image_or_images: Union[np.ndarray, List[np.ndarray]]) -> np.ndarray:
        """Not implemented for Ollama embeddings."""
        raise NotImplementedError("Ollama embeddings do not support image embeddings")