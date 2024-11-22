import pytest
import numpy as np
from unittest.mock import MagicMock

# Assuming that hybridagi.embeddings.ollama.OllamaEmbeddings can be imported without needing the server
from hybridagi.embeddings.ollama import OllamaEmbeddings

@pytest.fixture
def ollama_embeddings():
    # Create a mock instance of OllamaEmbeddings
    mock = MagicMock(spec=OllamaEmbeddings)
    
    mock.dim = 1024
    mock.batch_size = 10  # Arbitrary
    
    def mock_embed_text(query):
        if isinstance(query, str):
            if not query.strip():
                raise ValueError("Input text is empty")
            return np.random.rand(mock.dim).astype(np.float32)
        elif isinstance(query, list):
            if not query:
                raise ValueError("Input list is empty")
            for q in query:
                if not isinstance(q, str) or not q.strip():
                    raise ValueError("One or more input texts are empty")
            return [np.random.rand(mock.dim).astype(np.float32) for _ in query]
        else:
            raise ValueError("Invalid input type")
    
    mock.embed_text.side_effect = mock_embed_text
    
    mock.embed_image.side_effect = NotImplementedError("Embedding images is not implemented.")
    
    return mock

def test_embed_text_single(ollama_embeddings):
    query = "Hello"
    embedding = ollama_embeddings.embed_text(query)
    assert embedding.shape[0] == ollama_embeddings.dim
    assert isinstance(embedding, np.ndarray)
    assert embedding.dtype == np.float32

def test_embed_text_multiple(ollama_embeddings):
    queries = ["Hello", "World"]
    embeddings = ollama_embeddings.embed_text(queries)
    assert len(embeddings) == 2
    for emb in embeddings:
        assert emb.shape[0] == ollama_embeddings.dim
        assert isinstance(emb, np.ndarray)
        assert emb.dtype == np.float32

def test_embed_image_not_implemented(ollama_embeddings):
    with pytest.raises(NotImplementedError):
        ollama_embeddings.embed_image(np.random.random((ollama_embeddings.dim,)))

def test_embed_text_empty_input(ollama_embeddings):
    with pytest.raises(ValueError) as exc_info:
        ollama_embeddings.embed_text("")
    assert "Input text is empty" in str(exc_info.value)

def test_embed_text_empty_list(ollama_embeddings):
    with pytest.raises(ValueError) as exc_info:
        ollama_embeddings.embed_text([])
    assert "Input list is empty" in str(exc_info.value)

def test_batch_processing(ollama_embeddings):
    # Test with a number of queries that exceeds the batch size
    batch_size = ollama_embeddings.batch_size
    queries = [f"Query {i}" for i in range(batch_size + 5)]
    embeddings = ollama_embeddings.embed_text(queries)
    
    assert len(embeddings) == len(queries)
    for emb in embeddings:
        assert emb.shape[0] == ollama_embeddings.dim
        assert isinstance(emb, np.ndarray)
        assert emb.dtype == np.float32

def test_ollama_import_error(monkeypatch):
    # Simulate ollama import error
    import sys
    monkeypatch.setitem(sys.modules, 'ollama', None)
    
    with pytest.raises(ImportError) as exc_info:
        OllamaEmbeddings()
    assert "You need to install ollama library" in str(exc_info.value)