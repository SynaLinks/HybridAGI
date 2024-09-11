import dspy
import hybridagi.core.graph_program as gp
from hybridagi.core.datatypes import AgentState, Query
from hybridagi.memory.integration.falkordb import FalkorDBProgramMemory, FalkorDBTraceMemory
from hybridagi.modules.agents.graph_interpreter import GraphInterpreterAgent
from hybridagi.modules.agents.tools import SpeakTool
from dspy.utils.dummies import DummyLM
from hybridagi.embeddings.fake import FakeEmbeddings
from hybridagi.modules.retrievers.integration.falkordb import FalkorDBActionRetriever

def test_falkordb_action_retriever():    
    answers = ["Paris"]
    dspy.settings.configure(lm=DummyLM(answers=answers))
    
    main = gp.GraphProgram(
        name="main",
        description="The main program",
    )
        
    main.add(gp.Action(
        id="answer",
        purpose="Answer the Objective's question",
        tool="Speak",
        prompt="Please answer to the Objective's question",
    ))

    main.connect("start", "answer")
    main.connect("answer", "end")
    
    main.build()
    
    program_memory = FalkorDBProgramMemory(
        index_name="test_action_retriever",
        wipe_on_start=True,
    )
    
    trace_memory = FalkorDBTraceMemory(
        index_name="test_action_retriever",
        wipe_on_start=True,
    )
    
    program_memory.update(main)
    
    embeddings = FakeEmbeddings(dim=256)
    
    agent_state = AgentState()
    
    tools = [
        SpeakTool(
            agent_state=agent_state
        ),
    ]
    
    agent = GraphInterpreterAgent(
        program_memory = program_memory,
        trace_memory = trace_memory,
        embeddings = embeddings,
        agent_state = agent_state,
        tools = tools,
        debug = True,
    )
    
    input_query = Query(query="What is the capital of France?")
    agent_output = agent(input_query)
    
    retriever = FalkorDBActionRetriever(
        trace_memory = trace_memory,
        embeddings = embeddings,
        distance = "cosine",
        max_distance = 1.0,
        k = 5,
        reverse = True,
        reranker = None,
    )
    result = retriever(Query(query="French capital"))
    assert len(result.steps) > 0