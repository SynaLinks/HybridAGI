from hybridagi.memory.integration.falkordb.falkordb_document_memory import FalkorDBDocumentMemory
from hybridagi.embeddings.fake import FakeEmbeddings
import hybridagi.core.datatypes as dt
import pytest

@pytest.fixture
def falkordb_document_memory():
    embeddings = FakeEmbeddings(dim=250)
    return FalkorDBDocumentMemory(
        index_name="test_document",
        embeddings=embeddings,
        hostname="localhost",
        port=6379,
        username="",
        password="",
        indexed_label="Content",
        wipe_on_start=True,
        chunk_size=1024,
        chunk_overlap=0
    )

def test_falkordb_program_memory_empty(falkordb_document_memory):
    assert falkordb_document_memory is not None
    
def test_local_document_memory_update_one_doc(falkordb_document_memory):
    doc = dt.Document(text="This is a test text", metadata={"key": "value"})
    falkordb_document_memory.update(doc)
    assert falkordb_document_memory._documents[str(doc.id)] == doc
    assert falkordb_document_memory._documents[str(doc.id)].metadata == {"key": "value"}
    
def test_local_document_memory_update_same_doc(falkordb_document_memory):
    doc = dt.Document(text="This is a test text", metadata={"key": "value"})
    falkordb_document_memory.update(doc)
    doc.text = "Another text"
    doc.metadata["new_key"] = "new_value"
    falkordb_document_memory.update(doc)
    assert len(falkordb_document_memory._documents) == 1
    assert falkordb_document_memory._documents[str(doc.id)].metadata == {"key": "value", "new_key": "new_value"}

def test_local_document_memory_update_doc_metadata(falkordb_document_memory):
    doc = dt.Document(text="This is a test text", metadata={"key": "value"})
    falkordb_document_memory.update(doc)
    doc.metadata = {"updated_key": "updated_value"}
    falkordb_document_memory.update(doc)
    assert falkordb_document_memory._documents[str(doc.id)].metadata == {"updated_key": "updated_value"}
    
def test_local_document_memory_add_doc_list(falkordb_document_memory):
    doc_list = dt.DocumentList()
    doc_list.docs = [
        dt.Document(text="This is a test text"),
        dt.Document(text="This is another test text"),
    ]
    falkordb_document_memory.update(doc_list)
    assert len(falkordb_document_memory._documents) == 2
    
def test_local_document_memory_remove_one_doc(falkordb_document_memory):
    doc = dt.Document(text="This is a test text")
    falkordb_document_memory.update(doc)
    assert falkordb_document_memory._documents[str(doc.id)] == doc
    falkordb_document_memory.remove(doc.id)
    assert len(falkordb_document_memory._documents) == 0
    
def test_local_document_memory_remove_multiple_docs(falkordb_document_memory):
    doc_list = dt.DocumentList()
    doc_list.docs = [
        dt.Document(text="This is a test text"),
        dt.Document(text="This is another test text"),
    ]
    falkordb_document_memory.update(doc_list)
    assert len(falkordb_document_memory._documents) == 2
    ids = [d.id for d in doc_list.docs]
    falkordb_document_memory.remove(ids)
    assert len(falkordb_document_memory._documents) == 0
    
def test_local_document_memory_get_one_doc(falkordb_document_memory):
    doc = dt.Document(text="This is a test text", metadata={"key": "value"})
    falkordb_document_memory.update(doc)
    assert falkordb_document_memory._documents[str(doc.id)] == doc
    res = falkordb_document_memory.get(doc.id)
    assert len(res.docs) == 1
    retrieved_doc = res.docs[0]
    assert retrieved_doc.id == doc.id
    assert retrieved_doc.text == doc.text
    assert retrieved_doc.parent_id == doc.parent_id
    assert retrieved_doc.metadata == {"key": "value"}
    # Compare vectors element-wise if they exist
    if doc.vector is not None and retrieved_doc.vector is not None:
        assert all(abs(a - b) < 1e-6 for a, b in zip(doc.vector, retrieved_doc.vector))

def test_local_document_memory_search_with_metadata(falkordb_document_memory):
    doc1 = dt.Document(text="This is a test text", metadata={"category": "test"})
    doc2 = dt.Document(text="This is another test text", metadata={"category": "example"})
    falkordb_document_memory.update(dt.DocumentList(docs=[doc1, doc2]))
    
    results = falkordb_document_memory.search("test")
    assert len(results.docs) == 2
    for doc in results.docs:
        assert doc.metadata is not None
        assert "category" in doc.metadata

def test_local_document_memory_clear_with_metadata(falkordb_document_memory):
    doc = dt.Document(text="This is a test text", metadata={"key": "value"})
    falkordb_document_memory.update(doc)
    falkordb_document_memory.clear()
    assert len(falkordb_document_memory._documents) == 0
    assert len(falkordb_document_memory._embeddings) == 0
