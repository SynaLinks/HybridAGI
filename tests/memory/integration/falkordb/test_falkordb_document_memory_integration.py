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