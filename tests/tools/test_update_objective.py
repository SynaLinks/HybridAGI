import dspy
from dspy.utils.dummies import DummyLM
from hybridagi import GraphProgramInterpreter
from hybridagi.tools import UpdateObjectiveTool

def test_update_objective_tool():
    answers = ["test prediction"]
    dspy.settings.configure(lm=DummyLM(answers=answers))
    #TODO