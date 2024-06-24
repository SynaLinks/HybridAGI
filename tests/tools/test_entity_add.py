import dspy
from hybridagi import FakeEmbeddings
from hybridagi import FactMemory
from hybridagi.tools import EntityAddTool
from dspy.utils.dummies import DummyLM

def test_tool_with_lm():
    emb = FakeEmbeddings(dim=250)

    pred_answer = """[("Capital_of_England", "is equal to", "London"), ("Location_of_Westminster", "is", "London"), ("Part_of_London", "is", "Westminster")]"""
    extract_triple_answer = """[("Capital_of_England", "is equal to", "London"), ("Location_of_Westminster", "is", "London"), ("Part_of_London", "is", "Westminster")]"""
    dspy.settings.configure(lm=DummyLM(answers=[pred_answer, extract_triple_answer]))
    
    memory = FactMemory(
        index_name = "test",
        embeddings = emb,
        wipe_on_start = True,
    )

    tool = EntityAddTool(
        fact_memory = memory,
        embeddings = emb,
    )

    prediction = tool(
        objective = "test objective",
        context = "Nothing done yet",
        purpose = "test purpose",
        prompt = "test prompt",
        disable_inference = False,
    )

    assert prediction.message == "Processed document: 3 valid triplets added to FactMemory."

def test_tool_without_lm():
    emb = FakeEmbeddings(dim=250)
   
    memory = FactMemory(
        index_name = "test",
        embeddings = emb,
        wipe_on_start = True,
    )

    tool = EntityAddTool(
        fact_memory = memory,
        embeddings = emb,
    )

    prediction = tool(
        objective = "test objective",
        context = "Nothing done yet",
        purpose = "test purpose",
        prompt = """[("Capital_of_England", "is equal to", "London"), ("Location_of_Westminster", "is", "London"), ("Part_of_London", "is", "Westminster")]""",
        disable_inference = True,
    )

    assert prediction.message == "Processed document: 3 valid triplets added to FactMemory."
