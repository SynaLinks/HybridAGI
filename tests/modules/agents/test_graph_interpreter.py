import dspy
import hybridagi.core.graph_program as gp
from hybridagi.core.datatypes import AgentState, Query
from hybridagi.memory.integration.local import LocalProgramMemory
from hybridagi.modules.agents.graph_interpreter import GraphInterpreterAgent
from hybridagi.modules.agents.tools import SpeakTool

from dspy.utils.dummies import DummyLM

def test_graph_interpreter_one_action():
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
    
    program_memory = LocalProgramMemory(index_name="test")
    
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
    )
    
    input_query = Query(query="What is the capital of France?")
    agent_output = agent(input_query)
    assert agent_output.final_answer == "Paris"
    assert agent_output.finish_reason == "finished"
    
def test_graph_interpreter_two_actions():
    answers = ["The objective question is what is the capital of France, which is Paris","Paris"]
    dspy.settings.configure(lm=DummyLM(answers=answers))
    
    main = gp.GraphProgram(
        name="main",
        description="The main program",
    )
    
    main.add(gp.Action(
        id="elaborate",
        purpose="Elaborate to answer the Objective's question",
        tool="Speak",
        prompt="Please elaborate to answer the Objective's question",
    ))
        
    main.add(gp.Action(
        id="answer",
        purpose="Answer the Objective's question",
        tool="Speak",
        prompt="Please answer to the Objective's question",
    ))

    main.connect("start", "elaborate")
    main.connect("elaborate", "answer")
    main.connect("answer", "end")
    
    main.build()
    
    program_memory = LocalProgramMemory(index_name="test")
    
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
    )
    
    input_query = Query(query="What is the capital of France?")
    agent_output = agent(input_query)
    assert agent_output.final_answer == "Paris"
    assert agent_output.finish_reason == "finished"
    
def test_graph_interpreter_one_decision():
    answers = [" blabla \nChoice: Answer", "Paris"]
    dspy.settings.configure(lm=DummyLM(answers=answers))
    
    main=gp.GraphProgram(
        name="main",
        description="The main program",
    )
    
    main.add(gp.Decision(
        id = "is_objective_unclear",
        purpose = "Check if the Objective is unclear",
        question="Is the Objective's question still unclear?",
    ))
    
    main.add(gp.Action(
        id = "clarify",
        purpose = "Ask one question to clarify the Objective",
        tool = "AskUser",
        prompt = "Pick one question to clarify the Objective's question",
    ))
    
    main.add(gp.Action(
        id = "refine_objective",
        purpose = "Refine the Objective's question",
        tool = "UpdateObjective",
        prompt = "Please refine the Objective's question",
    ))
    
    main.add(gp.Action(
        id = "answer",
        purpose = "Answer the Objective's question",
        tool = "Speak",
        prompt = "Please answer to the Objective's question",
    ))
    
    main.connect("start", "is_objective_unclear")
    main.connect("is_objective_unclear", "clarify", label="Clarify")
    main.connect("is_objective_unclear", "answer", label="Answer")
    main.connect("clarify", "refine_objective")
    main.connect("refine_objective", "answer")
    main.connect("answer", "end")
    
    main.build()
    
    program_memory = LocalProgramMemory(index_name="test")
    
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
    )
    
    input_query = Query(query="What is the capital of France?")
    agent_output = agent(input_query)
    assert agent_output.final_answer == "Paris"
    assert agent_output.finish_reason == "finished"
    
def test_graph_interpreter_one_program():
    answers = [" blabla \nChoice: Answer", "Paris"]
    dspy.settings.configure(lm=DummyLM(answers=answers))
    
    clarify_objective = gp.GraphProgram(
        name = "clarify_objective",
        description = "Clarify the objective by asking question to the user",
    )

    clarify_objective.add(gp.Decision(
        id = "is_anything_unclear",
        purpose = "Check if the question is unclear",
        question = "Is the Objective's question still unclear?",
    ))

    clarify_objective.add(gp.Action(
        id = "ask_question",
        purpose = "Ask question to clarify the Objective",
        tool = "AskUser",
        prompt = "Pick one question to clarify the Objective's question",
    ))

    clarify_objective.add(gp.Action(
        id = "refine_objective",
        purpose = "Refine the question",
        tool = "UpdateObjective",
        prompt = "Refine the Objective's question",
    ))

    clarify_objective.connect("start", "is_anything_unclear")
    clarify_objective.connect("ask_question", "refine_objective")
    clarify_objective.connect("is_anything_unclear", "ask_question", label="Clarify")
    clarify_objective.connect("is_anything_unclear", "end", label="Answer")
    clarify_objective.connect("refine_objective", "end")

    clarify_objective.build()

    main = gp.GraphProgram(
        name="main",
        description="The main program",
    )

    main.add(gp.Program(
        id = "clarify_objective",
        purpose = "Clarify the Objective if needed",
        program = "clarify_objective"
    ))

    main.add(gp.Action(
        id = "answer",
        purpose = "Answer the Objective's question",
        tool = "Speak",
        prompt = "Answer the Objective's question",
    ))

    main.connect("start", "clarify_objective")
    main.connect("clarify_objective", "answer")
    main.connect("answer", "end")

    main.build()
    
    program_memory = LocalProgramMemory(index_name="test")
    
    program_memory.update(clarify_objective)
    program_memory.update(main)
    
    agent_state = AgentState()
    
    tools = [
        SpeakTool(
            agent_state=agent_state,
        ),
    ]
    
    agent = GraphInterpreterAgent(
        program_memory = program_memory,
        agent_state = agent_state,
        tools = tools,
    )
    
    input_query = Query(query="What is the capital of France?")
    agent_output = agent(input_query)
    assert agent_output.final_answer == "Paris"
    assert agent_output.finish_reason == "finished"