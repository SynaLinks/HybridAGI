import pytest
from unittest.mock import patch
from hybridagi.memory.integration.falkordb.falkordb_document_memory import FalkorDBDocumentMemory
from hybridagi.embeddings.fake import FakeEmbeddings
from hybridagi.core.datatypes import Document, DocumentList

@pytest.fixture
def memory():
    with patch('hybridagi.memory.integration.falkordb.falkordb_memory.FalkorDB') as MockFalkorDB:
        mock_falkordb = MockFalkorDB.return_value
        memory = FalkorDBDocumentMemory(
  index_name="test_index",
  embeddings=FakeEmbeddings(dim=250)
        )
        memory.hybridstore = mock_falkordb
        yield memory

def test_exist(memory):
    memory.hybridstore.query.return_value.result_set = [[1]]
    result = memory.exist("test_id")  
    assert result, f"Expected True, but got {result}"
    memory.hybridstore.query.assert_called_with(     
        "MATCH (d:Document {id: $id}) RETURN COUNT(d) AS count",
        params={"id": "test_id"}
    )

def test_exist_not_found(memory):
    memory.hybridstore.query.return_value.result_set = [[0]]
    assert not memory.exist("test_id")
    memory.hybridstore.query.assert_called_with(
        "MATCH (d:Document {id: $id}) RETURN COUNT(d) AS count",
        params={"id": "test_id"}
    )

def test_update_document(memory):
    doc = Document(id="test_id", text="test_text", parent_id=None, vector=[1.0, 2.0])
    memory.update(doc)
    memory.hybridstore.query.assert_called_with(
        "MERGE (d:Document {id: $id}) SET d.text = $text, d.parent_id = $parent_id, d.vector = $vector",
        params={"id": "test_id", "text": "test_text", "parent_id": None, "vector": [1.0, 2.0]}
    )

def test_update_document_list(memory):
    docs = DocumentList(docs=[Document(id="test_id", text="test_text", parent_id=None, vector=[1.0, 2.0])])
    memory.update(docs)
    memory.hybridstore.query.assert_called_with(
        "MERGE (d:Document {id: $id}) SET d.text = $text, d.parent_id = $parent_id, d.vector = $vector",
        params={"id": "test_id", "text": "test_text", "parent_id": None, "vector": [1.0, 2.0]}
    )

def test_remove_document(memory):
    memory.remove("test_id")
    memory.hybridstore.query.assert_called_with(
        "MATCH (d:Document {id: $id}) DETACH DELETE d",
        params={"id": "test_id"}
    )

def test_get_document(memory):
    memory.hybridstore.query.return_value.result_set = [[{"id": "test_id", "text": "test_text", "parent_id": None, "vector": [1.0, 2.0]}]]
    docs = memory.get("test_id")
    assert len(docs.docs) == 1
    assert docs.docs[0].id == "test_id"
    assert docs.docs[0].text == "test_text"
    assert docs.docs[0].parent_id is None
    assert docs.docs[0].vector == [1.0, 2.0]

def test_get_parents(memory):
    memory.hybridstore.query.return_value.result_set = [[{"id": "parent_id", "text": "parent_text", "parent_id": None, "vector": [3.0, 4.0]}]]
    parents = memory.get_parents("test_id")
    assert len(parents.docs) == 1
    assert parents.docs[0].id == "parent_id"
    assert parents.docs[0].text == "parent_text"
    assert parents.docs[0].parent_id is None
    assert parents.docs[0].vector == [3.0, 4.0]

def test_clear(memory):
    memory.clear()
    memory.hybridstore.query.assert_called_with(
        "MATCH (n:Document) DETACH DELETE n",
        params={}
    )
