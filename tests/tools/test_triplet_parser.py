import dspy
from hybridagi.tools import TripletParserTool
from dspy.utils.dummies import DummyLM

def test_triplet_parser_tool_with_lm():
    answers = """[("SynaLinks", "is a young French start-up", "founded in Toulouse in 2023")]"""

    dspy.settings.configure(lm=DummyLM(answers=answers))
    tool = TripletParserTool()

    prediction = tool(
        objective="test objective",
        context="Nothing done yet",
        purpose="test purpose",
        prompt="test prompt",
        disable_inference=False,
    )
    assert prediction.message == answers[0]

def test_triplet_parser_tool_without_lm():
    answers = """[("SynaLinks", "is a young French start-up", "founded in Toulouse in 2023")]"""

    tool = TripletParserTool()

    prediction = tool(
        objective="test objective",
        context="Nothing done yet",
        purpose="test purpose",
        prompt=answers,
        disable_inference=True,
    )
    assert prediction.message == answers