import pytest
from unittest.mock import patch
from uuid import UUID
from hybridagi.memory.integration.falkordb.falkordb_trace_memory import FalkorDBTraceMemory
from hybridagi.embeddings.fake import FakeEmbeddings

@pytest.fixture
def memory():
    with patch('hybridagi.memory.integration.falkordb.falkordb_memory.FalkorDB') as MockFalkorDB:
        mock_falkordb = MockFalkorDB.return_value
        memory = FalkorDBTraceMemory(
            index_name="test_trace_memory",
            embeddings=FakeEmbeddings(dim=128),
            graph_index="test_graph",
            hostname="localhost",
            port=6379
        )
        memory.hybridstore = mock_falkordb
        yield memory

def test_exist(memory):
    memory.hybridstore.query.return_value.result_set = [[1]]
    result = memory.exist(UUID("12345678-1234-5678-1234-567812345678"))
    assert result, f"Expected True, but got {result}"
    memory.hybridstore.query.assert_called_with(
        "MATCH (n:AgentStep {id: $index}) RETURN COUNT(n) AS count",
        params={"index": "12345678-1234-5678-1234-567812345678"}
    )

def test_exist_not_found(memory):
    memory.hybridstore.query.return_value.result_set = [[0]]
    assert not memory.exist(UUID("00000000-0000-0000-0000-000000000000"))
    memory.hybridstore.query.assert_called_with(
        "MATCH (n:AgentStep {id: $index}) RETURN COUNT(n) AS count",
        params={"index": "00000000-0000-0000-0000-000000000000"}
    )

def test_clear(memory):
    memory.clear()
    memory.hybridstore.query.assert_called_with(
        "MATCH (s:AgentStep) DETACH DELETE s",
        params={}
    )
