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
        prediction = None,
        log = "",
    )
    memory.commit(step)

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
    memory.commit(step2)


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