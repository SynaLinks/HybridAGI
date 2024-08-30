import pytest
import numpy as np
from hybridagi.embeddings.sentence_transformer import SentenceTransformerEmbeddings

@pytest.fixture
def sentence_transformer_embeddings():
    model_name = "all-MiniLM-L6-v2"  # Example model name
    dim = 384  # Example dimension for the model
    return SentenceTransformerEmbeddings(model_name_or_path=model_name, dim=dim)

def test_embed_text_single(sentence_transformer_embeddings):
    query = "Hello"
    embedding = sentence_transformer_embeddings.embed_text(query)
    assert embedding.shape[0] == sentence_transformer_embeddings.dim
    assert np.isclose(np.linalg.norm(embedding), 1.0, atol=1e-5)

def test_embed_text_multiple(sentence_transformer_embeddings):
    queries = ["Hello", "World"]
    embeddings = sentence_transformer_embeddings.embed_text(queries)
    assert len(embeddings) == 2
    for emb in embeddings:
        assert emb.shape[0] == sentence_transformer_embeddings.dim
        assert np.isclose(np.linalg.norm(emb), 1.0, atol=1e-5)

def test_embed_image_not_implemented(sentence_transformer_embeddings):
    with pytest.raises(NotImplementedError):
        sentence_transformer_embeddings.embed_image(np.random.random((sentence_transformer_embeddings.dim,)))

def test_embed_text_empty_input(sentence_transformer_embeddings):
    with pytest.raises(ValueError):
        sentence_transformer_embeddings.embed_text("")
