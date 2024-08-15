import pytest
from uuid import uuid4
from hybridagi.memory.integration.falkordb.falkordb_fact_memory import FalkorDBFactMemory
from hybridagi.core.datatypes import Entity, EntityList, Fact, FactList, Relationship
from hybridagi.embeddings.fake import FakeEmbeddings

@pytest.fixture
def memory():
    embeddings = FakeEmbeddings(dim=250)
    return FalkorDBFactMemory(
        index_name="test_fact",
        embeddings=embeddings,
        wipe_on_start=True
    )

def test_exist(memory):
    entity = Entity(id=str(uuid4()), name="Test Entity", label="TestLabel")
    memory.update(entity)
    assert memory.exist(entity.id) == True
    assert memory.exist(str(uuid4())) == False

def test_update_and_get_entities(memory):
    entity1 = Entity(id=str(uuid4()), name="Entity 1", label="TestLabel")
    entity2 = Entity(id=str(uuid4()), name="Entity 2", label="TestLabel")
    entity_list = EntityList(entities=[entity1, entity2])
    
    memory.update(entity_list)
    
    retrieved_entities = memory.get_entities([entity1.id, entity2.id])
    assert len(retrieved_entities.entities) == 2
    retrieved_names = {entity.name for entity in retrieved_entities.entities}
    assert retrieved_names == {"Entity 1", "Entity 2"}
    retrieved_ids = {str(entity.id) for entity in retrieved_entities.entities}
    assert retrieved_ids == {str(entity1.id), str(entity2.id)}

def test_update_and_get_facts(memory):
    entity1 = Entity(id=str(uuid4()), name="Entity 1", label="TestLabel")
    entity2 = Entity(id=str(uuid4()), name="Entity 2", label="TestLabel")
    relationship = Relationship(name="TestRelation")
    fact = Fact(id=str(uuid4()), subj=entity1, rel=relationship, obj=entity2)
    
    memory.update(fact)
    
    retrieved_facts = memory.get_facts(fact.id)
    assert len(retrieved_facts.facts) == 1
    assert retrieved_facts.facts[0].subj.name == "Entity 1"
    assert retrieved_facts.facts[0].obj.name == "Entity 2"
    assert retrieved_facts.facts[0].rel.name == "TestRelation"

def test_get_related_facts(memory):
    entity1 = Entity(id=str(uuid4()), name="Entity 1", label="TestLabel")
    entity2 = Entity(id=str(uuid4()), name="Entity 2", label="TestLabel")
    entity3 = Entity(id=str(uuid4()), name="Entity 3", label="TestLabel")
    relationship1 = Relationship(name="TestRelation1")
    relationship2 = Relationship(name="TestRelation2")
    fact1 = Fact(id=str(uuid4()), subj=entity1, rel=relationship1, obj=entity2)
    fact2 = Fact(id=str(uuid4()), subj=entity2, rel=relationship2, obj=entity3)
    
    memory.update(FactList(facts=[fact1, fact2]))
    
    related_facts = memory.get_related_facts(entity2.id)
    assert len(related_facts.facts) == 2
    
    related_facts_filtered = memory.get_related_facts(entity2.id, relation="TestRelation1")
    assert len(related_facts_filtered.facts) == 1
    assert related_facts_filtered.facts[0].rel.name == "TestRelation1"

def test_get_entities_by_type(memory):
    entity1 = Entity(id=str(uuid4()), name="Entity 1", label="TypeA")
    entity2 = Entity(id=str(uuid4()), name="Entity 2", label="TypeB")
    entity3 = Entity(id=str(uuid4()), name="Entity 3", label="TypeA")
    
    memory.update(EntityList(entities=[entity1, entity2, entity3]))
    
    type_a_entities = memory.get_entities_by_type("TypeA")
    assert len(type_a_entities.entities) == 2
    assert all(entity.label == "TypeA" for entity in type_a_entities.entities)

def test_search_entities(memory):
    entity1 = Entity(id=str(uuid4()), name="Apple", label="Fruit", description="A red fruit")
    entity2 = Entity(id=str(uuid4()), name="Banana", label="Fruit", description="A yellow fruit")
    entity3 = Entity(id=str(uuid4()), name="Carrot", label="Vegetable", description="An orange vegetable")
    
    memory.update(EntityList(entities=[entity1, entity2, entity3]))
    
    search_results = memory.search_entities("fruit")
    assert len(search_results.entities) == 2
    assert all(entity.label == "Fruit" for entity in search_results.entities)

def test_remove(memory):
    entity1 = Entity(id=str(uuid4()), name="Entity 1", label="TestLabel")
    entity2 = Entity(id=str(uuid4()), name="Entity 2", label="TestLabel")
    relationship = Relationship(name="TestRelation")
    fact = Fact(id=str(uuid4()), subj=entity1, rel=relationship, obj=entity2)
    
    memory.update(EntityList(entities=[entity1, entity2]))
    memory.update(fact)
    
    assert memory.exist(entity1.id) == True
    assert memory.exist(fact.id) == True
    
    memory.remove(entity1.id)
    memory.remove(fact.id)
    
    assert memory.exist(entity1.id) == False
    assert memory.exist(fact.id) == False
    assert memory.exist(entity2.id) == True

def test_clear(memory):
    entity1 = Entity(id=str(uuid4()), name="Entity 1", label="TestLabel")
    entity2 = Entity(id=str(uuid4()), name="Entity 2", label="TestLabel")
    relationship = Relationship(name="TestRelation")
    fact = Fact(id=str(uuid4()), subj=entity1, rel=relationship, obj=entity2)
    
    memory.update(EntityList(entities=[entity1, entity2]))
    memory.update(fact)
    
    assert memory.exist(entity1.id) == True
    assert memory.exist(entity2.id) == True
    assert memory.exist(fact.id) == True
    
    memory.clear()
    
    assert memory.exist(entity1.id) == False
    assert memory.exist(entity2.id) == False
    assert memory.exist(fact.id) == False
