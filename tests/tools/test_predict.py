import dspy
from hybridagi import FakeEmbeddings
from dspy.utils.dummies import DummyLM
from hybridagi.tools import PredictTool

def test_predict_tool():
    answers = ["test prediction"]
    dspy.settings.configure(lm=DummyLM(answers=answers))

    tool = PredictTool()
    
    prediction = tool(
        trace = "Nothing done yet",
        objective = "test objective",
        purpose = "test purpose",
        prompt = "test prompt",
        disable_inference = False,
        stop = None,
    )
    assert prediction.answer == "test prediction"

def test_predict_tool_without_inference():
    answers = ["test prediction"]
    dspy.settings.configure(lm=DummyLM(answers=answers))

    tool = PredictTool()
    
    prediction = tool(
        trace = "Nothing done yet",
        objective = "test objective",
        purpose = "test purpose",
        prompt = "test prompt",
        disable_inference = True,
        stop = None,
    )
    assert prediction.answer == "test prompt"




