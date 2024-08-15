import pytest
from unittest.mock import patch
from hybridagi.memory.integration.falkordb.falkordb_fact_memory import FalkorDBFactMemory
from hybridagi.embeddings.fake import FakeEmbeddings
from hybridagi.core.datatypes import Entity, Fact, Relationship

@pytest.fixture
def memory():
    with patch('hybridagi.memory.integration.falkordb.falkordb_memory.FalkorDB') as MockFalkorDB:
        mock_falkordb = MockFalkorDB.return_value
        memory = FalkorDBFactMemory(
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
        "MATCH (e:Entity {id: $id}) RETURN COUNT(e) AS count UNION ALL MATCH ()-[r:RELATION {id: $id}]->() RETURN COUNT(r) AS count",
        params={"id": "test_id"}
    )

def test_exist_not_found(memory):
    memory.hybridstore.query.return_value.result_set = [[0]]
    assert not memory.exist("test_id")
    memory.hybridstore.query.assert_called_with(
        "MATCH (e:Entity {id: $id}) RETURN COUNT(e) AS count UNION ALL MATCH ()-[r:RELATION {id: $id}]->() RETURN COUNT(r) AS count",
        params={"id": "test_id"}
    )

def test_update_entity(memory):
    entity = Entity(id="test_id", name="test_name", label="test_label", description="test_description", vector=[1.0, 2.0])
    memory.update(entity)
    memory.hybridstore.query.assert_called_with(
        "MERGE (e:Entity {id: $id}) SET e += $properties",
        params={"id": "test_id", "properties": {"name": "test_name", "label": "test_label", "description": "test_description", "vector": [1.0, 2.0]}}
    )

def test_update_fact(memory):
    subject = Entity(id="subject_id", name="subject_name", label="subject_label", description="subject_description", vector=[1.0, 2.0])
    object = Entity(id="object_id", name="object_name", label="object_label", description="object_description", vector=[3.0, 4.0])
    fact = Fact(id="fact_id", subj=subject, rel=Relationship(name="relation"), obj=object, vector=[5.0, 6.0])
    memory.update(fact)
    memory.hybridstore.query.assert_called_with(
        "MATCH (s:Entity {id: $subject_id}), (o:Entity {id: $object_id}) MERGE (s)-[r:RELATION {id: $id}]->(o) SET r += $properties",
        params={
            "id": "fact_id",
            "subject_id": "subject_id",
            "object_id": "object_id",
            "properties": {"name": "relation", "vector": [5.0, 6.0]}
        }
    )

def test_get_entities(memory):
    memory.hybridstore.query.return_value.result_set = [[{"id": "test_id", "name": "test_name", "label": "test_label", "description": "test_description", "vector": [1.0, 2.0]}]]
    entities = memory.get_entities("test_id")
    assert len(entities.entities) == 1
    assert entities.entities[0].id == "test_id"
    assert entities.entities[0].name == "test_name"
    assert entities.entities[0].label == "test_label"
    assert entities.entities[0].description == "test_description"
    assert entities.entities[0].vector == [1.0, 2.0]

def test_get_facts(memory):
    memory.hybridstore.query.return_value.result_set = [[
        {"id": "fact_id", "name": "relation", "vector": [5.0, 6.0]},
        {"id": "subject_id", "name": "subject_name", "label": "subject_label", "description": "subject_description", "vector": [1.0, 2.0]},
        {"id": "object_id", "name": "object_name", "label": "object_label", "description": "object_description", "vector": [3.0, 4.0]}
    ]]
    facts = memory.get_facts("fact_id")
    assert len(facts.facts) == 1
    assert facts.facts[0].id == "fact_id"
    assert facts.facts[0].subj.id == "subject_id"
    assert facts.facts[0].obj.id == "object_id"
    assert facts.facts[0].rel.name == "relation"

def test_clear(memory):
    memory.clear()
    memory.hybridstore.query.assert_called_with(
        "MATCH (n) DETACH DELETE n",
        params={}
    )
