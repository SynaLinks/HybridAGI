from typing import List
import pytest
from hybridagi.memory.integration.falkordb.falkordb_memory import FalkorDBMemory
from hybridagi.embeddings.fake import FakeEmbeddings

@pytest.fixture
def falkordb_memory():
    embeddings = FakeEmbeddings(dim=250)
    return FalkorDBMemory(
        index_name="test_index",
        graph_index="test_graph",
        embeddings=embeddings,
        hostname="localhost",
        port=6379,
        username="",
        password="",
        indexed_label="TestContent",
        wipe_on_start=True
    )

def test_initialization(falkordb_memory):
    assert isinstance(falkordb_memory, FalkorDBMemory)

def test_exist(falkordb_memory):
    # Assuming we have a method to add content for testing existence
    falkordb_memory.set_content("test_index", "test_content", "TestContent")
    assert falkordb_memory.exist("test_index", "TestContent")

def test_clear(falkordb_memory):
    falkordb_memory.set_content("test_index", "test_content", "TestContent")
    falkordb_memory.clear()
    assert not falkordb_memory.exist("test_index", "TestContent")

def test_set_and_get_content(falkordb_memory):
    falkordb_memory.set_content("test_index", "test_content", "TestContent")
    assert falkordb_memory.get_content_description("test_index", "TestContent") == "test_content"

def test_remove(falkordb_memory):
    falkordb_memory.set_content("test_index", "test_content", "TestContent")
    falkordb_memory.remove("test_index", "TestContent")
    assert not falkordb_memory.exist("test_index", "TestContent")
