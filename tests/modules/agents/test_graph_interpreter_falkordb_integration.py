import dspy
import hybridagi.core.graph_program as gp
from hybridagi.core.datatypes import AgentState, Query
from hybridagi.memory.integration.falkordb import FalkorDBProgramMemory
from hybridagi.modules.agents.graph_interpreter import GraphInterpreterAgent
from hybridagi.modules.agents.tools import SpeakTool
from dspy.utils.dummies import DummyLM
from hybridagi.embeddings.fake import FakeEmbeddings

def test_graph_interpreter_one_action_with_falkordb():
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
    
    embeddings=FakeEmbeddings(dim=128)
    
    program_memory = FalkorDBProgramMemory(
        index_name="test", 
        embeddings=embeddings,
        wipe_on_start=True,
    )
    
    program_memory.update(main)
    
    agent_state = AgentState()
    
    tools = [
        SpeakTool(
            agent_state=agent_state
        ),
    ]
    
    agent = GraphInterpreterAgent(
        program_memory = program_memory,
        agent_state = agent_state,
        tools = tools,
        embeddings = embeddings,
    )
    
    input_query = Query(query="What is the capital of France?")
    agent_output = agent(input_query)
    
    assert agent_output.final_answer == "Paris"
    assert agent_output.finish_reason == "finished"
