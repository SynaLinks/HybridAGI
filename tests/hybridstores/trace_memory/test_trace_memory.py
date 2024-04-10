import dspy
import json
from hybridagi import TraceMemory
from hybridagi import FakeEmbeddings
from hybridagi import AgentAction, AgentDecision, ProgramCall, ProgramEnd

def test_add_action_step():
    emb = FakeEmbeddings(dim=250)
    memory = TraceMemory(
        index_name="test",
        embeddings=emb,
        wipe_on_start=True,
    )

    step = AgentAction(
        hop = 0,
        objective = "test objective",
        purpose = "test purpose",
        tool = "TestTool",
        prompt = "This is a test prompt",
        prediction = dspy.Prediction(answer="test"),
        log = "",
    )
    index = memory.commit(step)
    assert memory.get_content(index) == json.dumps(dict(step.prediction), indent=2)


def test_add_decision_step():
    emb = FakeEmbeddings(dim=250)
    memory = TraceMemory(
        index_name="test",
        embeddings=emb,
        wipe_on_start=True,
    )

    step = AgentDecision(
        hop = 0,
        objective = "test objective",
        purpose = "test purpose",
        question = "This is a test question?",
        options = ["YES", "NO"],
        answer = "YES",
        log = "some log",
    )
    memory.commit(step)

def test_add_program_call_step():
    emb = FakeEmbeddings(dim=250)
    memory = TraceMemory(
        index_name="test",
        embeddings=emb,
        wipe_on_start=True,
    )

    step = ProgramCall(
        hop = 0,
        purpose = "test purpose",
        program = "main",
    )
    memory.commit(step)

def test_add_program_end_step():
    emb = FakeEmbeddings(dim=250)
    memory = TraceMemory(
        index_name="test",
        embeddings=emb,
        wipe_on_start=True,
    )

    step = ProgramEnd(
        hop = 0,
        program = "main",
    )
    memory.commit(step)


def test_add_two_step():
    emb = FakeEmbeddings(dim=250)
    memory = TraceMemory(
        index_name="test",
        embeddings=emb,
        wipe_on_start=True,
    )

    step1 = AgentAction(
        hop = 0,
        objective = "test objective",
        purpose = "test purpose",
        tool = "TestTool",
        prompt = "This is a test prompt",
        prediction = dspy.Prediction(answer="test1"),
        log = "",
    )
    step2 = AgentAction(
        hop = 0,
        objective = "test objective",
        purpose = "test purpose",
        tool = "TestTool",
        prompt = "This is a test prompt",
        prediction = dspy.Prediction(answer="test2"),
        log = "",
    )
    index1 = memory.commit(step1)
    index2 = memory.commit(step2)
    assert memory.get_content(index1) == json.dumps(dict(step1.prediction), indent=2)
    assert memory.get_content(index2) == json.dumps(dict(step2.prediction), indent=2)


def test_add_two_trace():
    emb = FakeEmbeddings(dim=250)
    memory = TraceMemory(
        index_name="test",
        embeddings=emb,
        wipe_on_start=True,
    )

    step1 = AgentAction(
        hop = 0,
        objective = "test objective",
        purpose = "test purpose",
        tool = "TestTool",
        prompt = "This is a test prompt",
        prediction = None,
        log = "",
    )
    step2 = AgentAction(
        hop = 0,
        objective = "test objective",
        purpose = "test purpose",
        tool = "TestTool",
        prompt = "This is a test prompt",
        prediction = None,
        log = "",
    )
    memory.commit(step1)
    memory.start_new_trace()
    memory.commit(step2)