import dspy
from hybridagi.tools import Tool
from dspy.utils.dummies import DummyLM

def greet(**kwargs):
    print(kwargs)
    name = kwargs["name"]
    message = f"hello {name}, nice to meet you!"
    output = {}
    output["message"] = message
    return output

def test_tool_with_lm():
    answers = ["Alice"]

    tool = Tool(
        name="Greet",
        signature="name -> message",
        instructions="greet a person",
        func = greet,
        lm = DummyLM(answers=answers))

    pred = tool(
        objective="Greet the User",
        context="Nothing done yet",
        purpose="Greet the User",
        prompt="Greet Alice",
    )
    assert pred.name == "Alice"
    assert pred.message == "hello Alice, nice to meet you!"

def test_tool_without_lm():

    answers = ["Alice"]

    dspy.settings.configure(lm=DummyLM(answers=answers))

    tool = Tool(
        name="Greet",
        signature="name -> message",
        instructions="greet a person",
        func = greet,
    )

    pred = tool(
        objective="Greet the User",
        context="Nothing done yet",
        purpose="Greet the User",
        prompt="Greet Alice",
    )
    assert pred.name == "Alice"
    assert pred.message == "hello Alice, nice to meet you!"
