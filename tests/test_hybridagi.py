import dspy
from hybridagi import HybridAGI
from dspy.utils.dummies import DummyLM

def test_hybridagi_init():
    agent = HybridAGI(agent_name="test_agent")

def test_hybridagi_add_programs():
    agent = HybridAGI(agent_name="test_agent")

    agent.add_programs_from_folders(["tests/test_programs"])

def test_hybridagi_execute():
    answers = ["Paris"]

    dspy.settings.configure(lm=DummyLM(answers=answers))

    agent = HybridAGI(agent_name="test_agent")

    agent.add_programs_from_folders(["tests/test_programs"])

    pred = agent.execute("What is the capital of France?")
    assert pred.final_answer == "Paris"