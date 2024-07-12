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
    
    answer = """[
        { "subject": "SynaLinks", "predicate": "is", "object": "a young French start-up founded in Toulouse in 2023" },
        { "subject": "SynaLinks", "predicate": "has", "object": "the mission to promote a responsible and pragmatic approach to general artificial intelligence" }
    ]"""
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
    
    assert prediction.message == "Processed document: 2 valid triplets added to FactMemory."

def test_entity_add_tool_without_llm():
    emb, memory = setup_memory_and_embeddings()
    
    answer = """
    1. (Subject: Capital_of_England, Predicate: is equal to, Object: London)
    2. (Subject: Location_of_Westminster, Predicate: is, Object: London)
    3. (Subject: Part_of_London, Predicate: is, Object: Westminster)
    """
    
    tool = EntityAddTool(
        fact_memory=memory,
        embeddings=emb,
    )
    
    prediction = tool(
        objective = answer,
        context = "Nothing done yet",
        purpose = "test purpose",
        prompt = "test prompt",
        disable_inference = True,
    )
    
    assert prediction.message == "Processed document: 3 valid triplets added to FactMemory."

# Add this new test function
def test_entity_add_tool_with_json_input():
    emb, memory = setup_memory_and_embeddings()
    
    json_input = """[
        { "subject": "SynaLinks", "predicate": "is", "object": "a young French start-up founded in Toulouse in 2023" }
    ]"""
    dspy.settings.configure(lm=DummyLM(answers=[json_input, json_input]))
    
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
    
    assert prediction.message == "Processed document: 1 valid triplets added to FactMemory."

# Add this new test function
def test_entity_add_tool_with_tuple_list_input():
    emb, memory = setup_memory_and_embeddings()
    
    tuple_list_input = """
    [(SynaLinks, founded in, Toulouse), (SynaLinks, mission, promote responsible and pragmatic approach to general artificial intelligence), (SynaLinks, integrate, deep learning models with symbolic AI models)]
    """
    dspy.settings.configure(lm=DummyLM(answers=[tuple_list_input, tuple_list_input]))
    
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

def test_entity_add_tool_with_numbered_list_input():
    emb, memory = setup_memory_and_embeddings()
    
    numbered_list_input = """
    Triplets: 
    1. ("SynaLinks", "founded_in", "2023")
    2. ("SynaLinks", "located_in", "Toulouse")
    """
    dspy.settings.configure(lm=DummyLM(answers=[numbered_list_input, numbered_list_input]))
    
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
    
    assert prediction.message == "Processed document: 2 valid triplets added to FactMemory."

def test_entity_add_tool_with_list_of_lists():
    emb, memory = setup_memory_and_embeddings()
    
    list_of_lists_input = """
    [["SynaLinks", "was founded", "in Toulouse in 2023"],
     ["SynaLinks", "has a mission", "to promote a responsible and pragmatic approach to general artificial intelligence"],
     ["At SynaLinks", "our approach aims to", "combine the efficiency of deep learning models with the transparency and explicability of symbolic models"],
     ["By combining these models", "we create", "more robust and ethical artificial intelligence systems"],
     ["SynaLinks", "works on", "cutting-edge technologies"],
     ["These technologies enable", "businesses", "to fully harness the potential of AI while retaining significant control over their systems"],
     ["SynaLinks", "works closely with", "clients to customize solutions"],
     ["Our neuro-symbolic approach", "offers", "the flexibility necessary to address the diverse requirements of businesses"]]
    """
    dspy.settings.configure(lm=DummyLM(answers=[list_of_lists_input, list_of_lists_input]))

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
    
    assert prediction.message == "Processed document: 8 valid triplets added to FactMemory.", f"Expected 8 triplets, but got: {prediction.message}"