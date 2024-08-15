import pytest
from unittest.mock import patch, MagicMock
from hybridagi.memory.integration.falkordb.falkordb_memory import FalkorDBMemory

@pytest.fixture
def memory():
    with patch('hybridagi.memory.integration.falkordb.falkordb_memory.FalkorDB') as MockFalkorDB:
        mock_falkordb = MockFalkorDB.return_value
        memory = FalkorDBMemory(
            index_name="test_index",
            graph_index="test_graph",
            embeddings=MagicMock(),
            hostname="localhost",
            port=6379,
            username="",
            password="",
            indexed_label="Content",
            wipe_on_start=False
        )
        memory.hybridstore = mock_falkordb
        yield memory

def test_exists(memory):
    memory.hybridstore.query.return_value.result_set = [[1]]
    assert memory.exists("test_index")

def test_exists_not_found(memory):
    memory.hybridstore.query.return_value.result_set = [[0]]
    assert not memory.exists("test_index")

def test_clear(memory):
    memory.clear()
    memory.hybridstore.delete.assert_called_once()

def test_init_with_wipe_on_start():
    with patch('hybridagi.memory.integration.falkordb.falkordb_memory.FalkorDB') as MockFalkorDB:
        mock_falkordb = MockFalkorDB.return_value
        memory = FalkorDBMemory(
            index_name="test_index",
            graph_index="test_graph",
            embeddings=MagicMock(),
            hostname="localhost",
            port=6379,
            username="",
            password="",
            indexed_label="Content",
            wipe_on_start=True
        )
        mock_falkordb.select_graph.return_value.delete.assert_called_once()
