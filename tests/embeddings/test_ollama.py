import pytest
import numpy as np
from hybridagi.embeddings.ollama import OllamaEmbeddings

@pytest.fixture
def ollama_embeddings():
    model_name = "mxbai-embed-large:latest" # default
    dim = 1024  # default for ^ that model
    return OllamaEmbeddings(model_name=model_name, dim=dim)

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
    with pytest.raises(ValueError):
        ollama_embeddings.embed_text("")

def test_embed_text_empty_list(ollama_embeddings):
    with pytest.raises(ValueError):
        ollama_embeddings.embed_text([])

def test_batch_processing(ollama_embeddings):
    # Nice trick: test with a number of queries that exceeds the batch size
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