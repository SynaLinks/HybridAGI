from hybridagi.memory.integration.local.local_document_memory import LocalDocumentMemory
import hybridagi.core.datatypes as dt

def test_local_document_memory_empty():
    mem = LocalDocumentMemory(index_name="test")
    
def test_local_document_memory_update_one_doc():
    mem = LocalDocumentMemory(index_name="test")
    doc = dt.Document(text="This is a test text")
    mem.update(doc)
    assert mem._documents[str(doc.id)] == doc
    
def test_local_document_memory_update_same_doc():
    mem = LocalDocumentMemory(index_name="test")
    doc = dt.Document(text="This is a test text")
    mem.update(doc)
    doc.text = "Another text"
    mem.update(doc)
    assert len(mem._documents) == 1
    
def test_local_document_memory_add_doc_list():
    mem = LocalDocumentMemory(index_name="test")
    doc_list = dt.DocumentList()
    doc_list.docs = [
        dt.Document(text="This is a test text"),
        dt.Document(text="This is another test text"),
    ]
    mem.update(doc_list)
    assert len(mem._documents) == 2
    
def test_local_document_memory_remove_one_doc():
    mem = LocalDocumentMemory(index_name="test")
    doc = dt.Document(text="This is a test text")
    mem.update(doc)
    assert mem._documents[str(doc.id)] == doc
    mem.remove(doc.id)
    assert len(mem._documents) == 0
    
def test_local_document_memory_remove_multiple_docs():
    mem = LocalDocumentMemory(index_name="test")
    doc_list = dt.DocumentList()
    doc_list.docs = [
        dt.Document(text="This is a test text"),
        dt.Document(text="This is another test text"),
    ]
    mem.update(doc_list)
    assert len(mem._documents) == 2
    ids = [d.id for d in doc_list.docs]
    mem.remove(ids)
    assert len(mem._documents) == 0
    
def test_local_document_memory_get_one_doc():
    mem = LocalDocumentMemory(index_name="test")
    doc = dt.Document(text="This is a test text")
    mem.update(doc)
    assert mem._documents[str(doc.id)] == doc
    res = mem.get(doc.id)
    assert res.docs[0] == doc
    