from hybridagi.memory.integration.falkordb.falkordb_program_memory import FalkorDBProgramMemory
from hybridagi.embeddings.fake import FakeEmbeddings
from hybridagi.core.graph_program import GraphProgram, Action, Control
import hybridagi.core.graph_program as gp
import pytest
import uuid

@pytest.fixture
def falkordb_program_memory():
    embeddings = FakeEmbeddings(dim=250)
    return FalkorDBProgramMemory(
        index_name="test_index_01",
        embeddings=embeddings,
        hostname="localhost",
        port=6379,
        username="",
        password="",
        indexed_label="Program",
        wipe_on_start=True,
    )

def test_falkordb_program_memory_empty(falkordb_program_memory):
    assert falkordb_program_memory is not None
    assert falkordb_program_memory.get_all_programs().progs == []

def test_init(falkordb_program_memory):
    assert falkordb_program_memory is not None

def test_local_program_memory_update_one_prog(falkordb_program_memory):
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
    
    falkordb_program_memory.update(main)

    assert falkordb_program_memory._programs["main"] == main


def test_local_program_memory_remove_one_prog(falkordb_program_memory):
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
    
    falkordb_program_memory.update(main)
    
    assert falkordb_program_memory._programs["main"] == main
    falkordb_program_memory.remove("main")
    assert len(falkordb_program_memory._programs) == 0
    
def test_local_program_memory_update_dependencies_prog(falkordb_program_memory):
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
    
    falkordb_program_memory.update(clarify_objective)
    falkordb_program_memory.update(main)

    assert falkordb_program_memory.depends_on("main", "clarify_objective")

def test_is_protected(falkordb_program_memory):
    # Test with a reserved name
    assert falkordb_program_memory.is_protected("main") == True
    assert falkordb_program_memory.is_protected("playground") == True
    
    # Test with a non-reserved name
    assert falkordb_program_memory.is_protected("test_program") == False
    
    # Test with a program that "main" depends on
    main = gp.GraphProgram(name="main", description="The main program")
    dependent_program = gp.GraphProgram(name="dependent_program", description="A program that main depends on")
    
    # Build dependent_program
    dependent_program.add(gp.Action(id="dummy_action", purpose="Dummy action", tool="DummyTool", prompt="Dummy prompt"))
    dependent_program.connect("start", "dummy_action")
    dependent_program.connect("dummy_action", "end")
    dependent_program.build()

    # Build main program
    main.add(gp.Program(id="dependent", purpose="Use dependent program", program="dependent_program"))
    main.connect("start", "dependent")
    main.connect("dependent", "end")
    main.build()
    
    falkordb_program_memory.update(dependent_program)
    falkordb_program_memory.update(main)
    
    assert falkordb_program_memory.is_protected("dependent_program") == True
