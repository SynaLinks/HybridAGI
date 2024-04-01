import dspy
from dspy.utils.dummies import DummyLM
from hybridagi.tools import PredictTool

def test_predict_tool():
    answers = ["test prediction"]
    dspy.settings.configure(lm=DummyLM(answers=answers))

    tool = PredictTool()
    
    prediction = tool(
        objective = "test objective",
        context = "Nothing done yet",
        purpose = "test purpose",
        prompt = "test prompt",
        disable_inference = False,
    )
    assert prediction.answer == "test prediction"

def test_predict_tool_without_inference():
    answers = ["test prediction"]
    dspy.settings.configure(lm=DummyLM(answers=answers))

    tool = PredictTool()
    
    prediction = tool(
        objective = "test objective",
        context = "Nothing done yet",
        purpose = "test purpose",
        prompt = "test prompt",
        disable_inference = True,
    )
    assert prediction.answer == "test prompt"




