import pytest
import numpy as np
from hybridagi.embeddings.fake import FakeEmbeddings

@pytest.fixture
def fake_embeddings():
    dim = 10
    return FakeEmbeddings(dim=dim, normalize_embeddings=True)

def test_embed_text_single(fake_embeddings):
    query = "Hello"
    embedding = fake_embeddings.embed_text(query)
    assert embedding.shape[0] == fake_embeddings.dim
    assert np.isclose(np.linalg.norm(embedding), 1.0, atol=1e-5)

def test_embed_text_multiple(fake_embeddings):
    queries = ["Hello", "World"]
    embeddings = fake_embeddings.embed_text(queries)
    assert len(embeddings) == 2
    for emb in embeddings:
        assert emb.shape[0] == fake_embeddings.dim
        assert np.isclose(np.linalg.norm(emb), 1.0, atol=1e-5)

def test_embed_image_single(fake_embeddings):
    image = np.random.random((fake_embeddings.dim,))
    embedding = fake_embeddings.embed_image(image)
    assert embedding.shape[0] == fake_embeddings.dim
    assert np.isclose(np.linalg.norm(embedding), 1.0, atol=1e-5)

def test_embed_image_multiple(fake_embeddings):
    images = [np.random.random((fake_embeddings.dim,)) for _ in range(2)]
    embeddings = fake_embeddings.embed_image(images)
    assert len(embeddings) == 2
    for emb in embeddings:
        assert emb.shape[0] == fake_embeddings.dim
        assert np.isclose(np.linalg.norm(emb), 1.0, atol=1e-5)
