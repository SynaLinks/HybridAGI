import dspy
from hybridagi.tools import TripletParserTool
from dspy.utils.dummies import DummyLM

def test_triplet_parser_tool_with_lm():
    answer = """[("Capital_of_England", "is equal to", "London"), ("Location_of_Westminster", "is", "London"), ("Part_of_London", "is", "Westminster")]"""
    # answer = """(Subject: SynaLinks, Predicate: is a young French start-up, Object: founded in Toulouse in 2023)"""
    dspy.settings.configure(lm=DummyLM(answers=[answer]))
    
    tool = TripletParserTool()

    prediction = tool(
        objective = "test objective",
        context = "Nothing done yet",
        purpose = "test purpose",
        prompt = "test prompt",
        disable_inference = False,
    )

    assert prediction.message == eval(answer)

def test_triplet_parser_tool_without_lm():
    answer = """[("Capital_of_England", "is equal to", "London"), ("Location_of_Westminster", "is", "London"), ("Part_of_London", "is", "Westminster")]"""

    tool = TripletParserTool()

    prediction = tool(
        objective = "test objective",
        context = "Nothing done yet",
        purpose = "test purpose",
        prompt = answer,
        disable_inference = True,
    )

    assert prediction.message == eval(answer)