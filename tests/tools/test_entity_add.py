import dspy
from hybridagi import FakeEmbeddings
from hybridagi import FactMemory
from hybridagi.tools import EntityAddTool
from dspy.utils.dummies import DummyLM

def setup_memory_and_embeddings():
    emb = FakeEmbeddings(dim=250)
    memory = FactMemory(
        index_name="test",
        embeddings=emb,
        wipe_on_start=True,
    )
    return emb, memory

def test_entity_add_tool_with_llm_list_input():
    emb, memory = setup_memory_and_embeddings()

    answer = """[("Capital_of_England", "is equal to", "London"), ("Location_of_Westminster", "is", "London"), ("Part_of_London", "is", "Westminster")]"""
    dspy.settings.configure(lm=DummyLM(answers=[answer, answer]))

    tool = EntityAddTool(
        fact_memory=memory,
        embeddings=emb,
    )

    prediction = tool(
        objective = "test objective",
        context = "Nothing done yet",
        purpose = "test purpose",
        prompt = "test prompt",
        disable_inference = False,
    )

    assert prediction.message == "Processed document: 3 valid triplets added to FactMemory."

def test_entity_add_tool_without_llm():
    emb, memory = setup_memory_and_embeddings()
    
    answer = """[("Capital_of_England", "is equal to", "London"), ("Location_of_Westminster", "is", "London"), ("Part_of_London", "is", "Westminster")]"""
    
    tool = EntityAddTool(
        fact_memory=memory,
        embeddings=emb,
    )

    prediction = tool(
        objective = "test objective",
        context = "Nothing done yet",
        purpose = "test purpose",
        prompt = answer,
        disable_inference = True,
    )

    assert prediction.message == "Processed document: 3 valid triplets added to FactMemory."