from hybridagi.memory.integration.falkordb.falkordb_document_memory import FalkorDBDocumentMemory
from hybridagi.embeddings.fake import FakeEmbeddings
from hybridagi.core.datatypes import Document, DocumentList

def test_falkordb_program_memory_empty():
    document_memory = FalkorDBDocumentMemory(index_name="test_doc_memory_constructor")

def test_local_document_memory_update_one_doc():
    document_memory = FalkorDBDocumentMemory(index_name="test_doc_update_one")
    doc = Document(text="This is a test text")
    document_memory.update(doc)
    assert document_memory.exist(doc.id)
    
def test_local_document_memory_get_one_doc():
    document_memory = FalkorDBDocumentMemory(index_name="test_get_one_doc")
    doc = Document(text="This is a test text")
    document_memory.update(doc)
    result_doc = document_memory.get(doc.id).docs[0]
    assert len(document_memory.get(doc.id).docs) == 1
    assert result_doc.id == doc.id
    assert result_doc.text == doc.text
    assert result_doc.parent_id == doc.parent_id
    assert result_doc.metadata == doc.metadata
    
def test_local_document_memory_override_doc():
    document_memory = FalkorDBDocumentMemory(index_name="test_override_doc")
    doc = Document(text="This is a test text")
    document_memory.update(doc)
    doc.text = "Another text"
    document_memory.update(doc)
    result_doc = document_memory.get(doc.id).docs[0]
    assert len(document_memory.get(doc.id).docs) == 1
    assert result_doc.text == "Another text"
    
def test_local_document_memory_update_doc_metadata():
    document_memory = FalkorDBDocumentMemory(index_name="test_update_doc_metadata")
    doc = Document(text="This is a test text", metadata={"key": "value"})
    document_memory.update(doc)
    result_doc = document_memory.get(doc.id).docs[0]
    assert result_doc.id == doc.id
    assert result_doc.text == doc.text
    assert result_doc.parent_id == doc.parent_id
    assert result_doc.metadata == {"key": "value"}

def test_local_document_memory_add_doc_list():
    document_memory = FalkorDBDocumentMemory(index_name="test_update_doc_metadata")
    doc_list = DocumentList()
    doc_list.docs = [
        Document(text="This is a test text"),
        Document(text="This is another test text"),
    ]
    document_memory.update(doc_list)
    result_list = document_memory.get([d.id for d in doc_list.docs])
    assert doc_list.docs[0] == result_list.docs[0]
    assert doc_list.docs[1] == result_list.docs[1]
    
# def test_local_document_memory_remove_one_doc(falkordb_document_memory):
#     doc = dt.Document(text="This is a test text")
#     falkordb_document_memory.update(doc)
#     assert falkordb_document_memory._documents[str(doc.id)] == doc
#     falkordb_document_memory.remove(doc.id)
#     assert len(falkordb_document_memory._documents) == 0
    
# def test_local_document_memory_remove_multiple_docs(falkordb_document_memory):
#     doc_list = dt.DocumentList()
#     doc_list.docs = [
#         dt.Document(text="This is a test text"),
#         dt.Document(text="This is another test text"),
#     ]
#     falkordb_document_memory.update(doc_list)
#     assert len(falkordb_document_memory._documents) == 2
#     ids = [d.id for d in doc_list.docs]
#     falkordb_document_memory.remove(ids)
#     assert len(falkordb_document_memory._documents) == 0
    
# def test_local_document_memory_get_one_doc(falkordb_document_memory):
#     doc = dt.Document(text="This is a test text", metadata={"key": "value"})
#     falkordb_document_memory.update(doc)
#     assert falkordb_document_memory._documents[str(doc.id)] == doc
#     res = falkordb_document_memory.get(doc.id)
#     assert len(res.docs) == 1
#     retrieved_doc = res.docs[0]
#     assert retrieved_doc.id == doc.id
#     assert retrieved_doc.text == doc.text
#     assert retrieved_doc.parent_id == doc.parent_id
#     assert retrieved_doc.metadata == {"key": "value"}
#     # Compare vectors element-wise if they exist
#     if doc.vector is not None and retrieved_doc.vector is not None:
#         assert all(abs(a - b) < 1e-6 for a, b in zip(doc.vector, retrieved_doc.vector))
