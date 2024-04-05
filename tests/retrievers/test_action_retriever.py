from hybridagi import (
    FakeEmbeddings,
    TraceMemory,
    AgentAction,
    ActionRetriever,
)

def test_forward():
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

    retriever = ActionRetriever(
        trace_memory = memory,
        embeddings = emb,
        distance_threshold = 100.0,
    )

    assert len(retriever.forward("test").past_actions) == 1