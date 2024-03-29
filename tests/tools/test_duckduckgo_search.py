import dspy
import time
from dspy.utils.dummies import DummyLM
from hybridagi.tools import DuckDuckGoSearchTool

def test_duckduckgo_search_tool():
    answers = ["HybridAGI framework on github"]
    dspy.settings.configure(lm=DummyLM(answers=answers))

    tool = DuckDuckGoSearchTool()
    time.sleep(1)
    prediction = tool(
        trace = "Nothing done yet",
        objective = "test objective",
        purpose = "test purpose",
        prompt = "test prompt",
        disable_inference = False,
        stop = None,
    )
    assert prediction.query == "HybridAGI framework on github"
    assert len(prediction.results) > 0

def test_duckduckgo_search_tool_without_inference():
    
    answers = ["test prediction"]
    dspy.settings.configure(lm=DummyLM(answers=answers))

    tool = DuckDuckGoSearchTool()
    time.sleep(1)
    prediction = tool(
        trace = "Nothing done yet",
        objective = "test objective",
        purpose = "test purpose",
        prompt = "HybridAGI framework on github",
        disable_inference = True,
        stop = None,
    )
    assert prediction.query == "HybridAGI framework on github"
    assert len(prediction.results) > 0




