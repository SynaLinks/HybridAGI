from hybridagi.memory.integration.falkordb.falkordb_program_memory import FalkorDBProgramMemory
from hybridagi.embeddings.fake import FakeEmbeddings
from hybridagi.core.graph_program import GraphProgram, Action, Control
import hybridagi.core.graph_program as gp
import pytest
import uuid

def test_local_program_memory_constructor():
    program_memory = FalkorDBProgramMemory(index_name="test_prog_memory_constructor", wipe_on_start=True)

def test_falkorDB_program_memory_update_one_prog():
    program_memory = FalkorDBProgramMemory(index_name="test_update_one_prog", wipe_on_start=True)
    
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
    
    program_memory.update(main)
    assert program_memory.exist("main")
    
def test_falkorDB_program_memory_get_one_prog():
    program_memory = FalkorDBProgramMemory(index_name="test_get_one_prog", wipe_on_start=True)
    
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
    
    program_memory.update(main)
    result_prog = program_memory.get("main").progs[0]
    assert result_prog.name == main.name
    assert result_prog.to_cypher() == main.to_cypher()
    assert result_prog.metadata == main.metadata
    
def test_falkorDB_program_memory_override_one_prog():
    program_memory = FalkorDBProgramMemory(index_name="test_override_one_prog", wipe_on_start=True)
    
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
    
    program_memory.update(main)
    assert program_memory.exist("main")
    program_memory.update(main)
    assert program_memory.exist("main")
    assert len(program_memory.get("main").progs) == 1
    
def test_falkorDB_program_memory_update_one_embedded_prog():
    embeddings = FakeEmbeddings(dim=250)
    program_memory = FalkorDBProgramMemory(index_name="test_update_one_prog_with_embeddings", wipe_on_start=True)
    
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
    main.vector = embeddings.embed_text("test")
    
    program_memory.update(main)
    assert program_memory.exist("main")
    
def test_falkorDB_program_memory_remove_one_prog():
    program_memory = FalkorDBProgramMemory(index_name="test_remove_one_prog", wipe_on_start=True)
    
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
    
    program_memory.update(main)
    
    assert program_memory.exist("main")
    program_memory.remove("main")
    assert not program_memory.exist("main")
    
def test_local_program_memory_update_dependencies_prog():
    program_memory = FalkorDBProgramMemory(index_name="test_dependency", wipe_on_start=True)
    
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
    
    program_memory.update(main)
    program_memory.update(clarify_objective)

    assert program_memory.depends_on("main", "clarify_objective")
    
def test_local_program_memory_protected_prog():
    program_memory = FalkorDBProgramMemory(index_name="test_protected", wipe_on_start=True)
    
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
    
    program_memory.update(main)
    program_memory.update(clarify_objective)

    assert program_memory.is_protected("main")
    assert program_memory.is_protected("clarify_objective")