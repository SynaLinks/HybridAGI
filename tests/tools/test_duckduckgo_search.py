import dspy
from dspy.utils.dummies import DummyLM
from hybridagi.tools import DuckDuckGoSearchTool

def test_duckduckgo_search_tool():
    answers = ["HybridAGI framework on github"]
    dspy.settings.configure(lm=DummyLM(answers=answers))

    tool = DuckDuckGoSearchTool()
    prediction = tool(
        objective = "test objective",
        context = "Nothing done yet",
        purpose = "test purpose",
        prompt = "test prompt",
        disable_inference = False,
    )
    assert prediction.search_query == "HybridAGI framework on github"
    assert len(prediction.results) > 0

def test_duckduckgo_search_tool_without_inference():
    
    answers = ["test prediction"]
    dspy.settings.configure(lm=DummyLM(answers=answers))

    tool = DuckDuckGoSearchTool()
    prediction = tool(
        objective = "test objective",
        context = "Nothing done yet",
        purpose = "test purpose",
        prompt = "HybridAGI framework on github",
        disable_inference = True,
    )
    assert prediction.search_query == "HybridAGI framework on github"
    assert len(prediction.results) > 0




