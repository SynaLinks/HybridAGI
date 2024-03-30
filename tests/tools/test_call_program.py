import dspy
from dspy.utils.dummies import DummyLM
from hybridagi import FakeEmbeddings
from hybridagi import ProgramMemory
from hybridagi import AgentState
from hybridagi.tools import CallProgramTool
from hybridagi import GraphProgramInterpreter

def test_call_program_tool():
    answers = ["subprogram"]
    dspy.settings.configure(lm=DummyLM(answers=answers))
    emb = FakeEmbeddings(dim=250)

    memory = ProgramMemory(
        index_name = "test",
        embeddings = emb,
        wipe_on_start = True,
    )

    program = \
"""
// @desc: Test the call of a subprogram
CREATE
(start:Control {name:"Start"}),
(answer:Action {
    name: "Answer the objective's question",
    tool: "Predict",
    prompt: "You are an helpfull assistant, please answer the objective's question"
}),
(end:Control {name:"End"}),
(start)-[:NEXT]->(answer),
(answer)-[:NEXT]->(end)
"""
    program_name = "main"

    subprogram = \
"""
// @desc: Test subprogram
CREATE
(start:Control {name:"Start"}),
(end:Control {name:"End"}),
(start)-[:NEXT]->(end)
"""
    subprogram_name = "subprogram"

    memory.add_texts(
        texts = [program, subprogram],
        ids = [program_name, subprogram_name],
    )

    agent_state = AgentState()

    tools = [
        CallProgramTool(
            program_memory = memory,
            agent_state = agent_state,
        )
    ]

    interpreter = GraphProgramInterpreter(
        program_memory = memory,
        agent_state = agent_state,
        tools = tools
    )

    interpreter.start("test objective")

    print(interpreter.agent_state.program_stack)
    
    prediction = tools[0](
        objective = "test objective",
        context = "Nothing done yet",
        purpose = "test purpose",
        prompt = "test prompt",
        disable_inference = False,
    )
    print(interpreter.agent_state.program_stack)
    assert prediction.selected_program == "subprogram"
    assert prediction.observation == "Successfully called"

def test_call_program_tool_protected():
    answers = ["subprogram"]
    dspy.settings.configure(lm=DummyLM(answers=answers))
    emb = FakeEmbeddings(dim=250)

    memory = ProgramMemory(
        index_name = "test",
        embeddings = emb,
        wipe_on_start = True,
    )

    program = \
"""
// @desc: Test the call of a subprogram
CREATE
(start:Control {name:"Start"}),
(call_subprogram:Program {
    name: "Call a subprogram",
    program: "subprogram"
}),
(end:Control {name:"End"}),
(start)-[:NEXT]->(call_subprogram),
(call_subprogram)-[:NEXT]->(end)
"""
    program_name = "main"

    subprogram = \
"""
// @desc: Test subprogram
CREATE
(start:Control {name:"Start"}),
(end:Control {name:"End"}),
(start)-[:NEXT]->(end)
"""
    subprogram_name = "subprogram"

    memory.add_texts(
        texts = [program, subprogram],
        ids = [program_name, subprogram_name],
    )

    agent_state = AgentState()

    tool = CallProgramTool(
        program_memory = memory,
        agent_state = agent_state,
    )
    
    prediction = tool(
        objective = "test objective",
        context = "Nothing done yet",
        purpose = "test purpose",
        prompt = "test prompt",
        disable_inference = False,
    )
    assert prediction.selected_program == "subprogram"
    assert prediction.observation == "Error occured: Trying to call a protected program"


def test_call_program_tool_non_existant():
    answers = ["subprogram"]
    dspy.settings.configure(lm=DummyLM(answers=answers))
    emb = FakeEmbeddings(dim=250)

    memory = ProgramMemory(
        index_name = "test",
        embeddings = emb,
        wipe_on_start = True,
    )

    program = \
"""
// @desc: Test the call of a subprogram
CREATE
(start:Control {name:"Start"}),
(answer:Action {
    name: "Answer the objective's question",
    tool: "Predict",
    prompt: "You are an helpfull assistant, please answer the objective's question"
}),
(end:Control {name:"End"}),
(start)-[:NEXT]->(answer),
(answer)-[:NEXT]->(end)
"""
    program_name = "main"

    memory.add_texts(
        texts = [program],
        ids = [program_name],
    )

    agent_state = AgentState()

    tools = [
        CallProgramTool(
            program_memory = memory,
            agent_state = agent_state,
        )
    ]

    interpreter = GraphProgramInterpreter(
        program_memory=memory,
        agent_state=agent_state,
        tools=tools
    )

    interpreter.start("test objective")

    prediction = tools[0](
        objective = "test objective",
        context = "Nothing done yet",
        purpose = "test purpose",
        prompt = "test prompt",
        disable_inference = False,
    )
    assert prediction.selected_program == "subprogram"
    assert prediction.observation == "Error occured: This program does not exist, verify its name"


def test_call_program_without_inference():
    answers = ["subprogram"]
    dspy.settings.configure(lm=DummyLM(answers=answers))
    emb = FakeEmbeddings(dim=250)

    memory = ProgramMemory(
        index_name = "test",
        embeddings = emb,
        wipe_on_start = True,
    )

    program = \
"""
// @desc: Test the call of a subprogram
CREATE
(start:Control {name:"Start"}),
(answer:Action {
    name: "Answer the objective's question",
    tool: "Predict",
    prompt: "You are an helpfull assistant, please answer the objective's question"
}),
(end:Control {name:"End"}),
(start)-[:NEXT]->(answer),
(answer)-[:NEXT]->(end)
"""
    program_name = "main"

    subprogram = \
"""
// @desc: Test subprogram
CREATE
(start:Control {name:"Start"}),
(end:Control {name:"End"}),
(start)-[:NEXT]->(end)
"""
    subprogram_name = "subprogram"

    memory.add_texts(
        texts = [program, subprogram],
        ids = [program_name, subprogram_name],
    )

    agent_state = AgentState()

    tools = [
        CallProgramTool(
            program_memory = memory,
            agent_state = agent_state,
        )
    ]

    interpreter = GraphProgramInterpreter(
        program_memory=memory,
        agent_state=agent_state,
        tools=tools
    )

    interpreter.start("test objective")

    print(interpreter.agent_state.program_stack)
    
    prediction = tools[0](
        objective = "test objective",
        context = "Nothing done yet",
        purpose = "test purpose",
        prompt = "test prompt",
        disable_inference = True,
    )
    assert prediction.selected_program == "test prompt"