from hybridagi.memory.integration.local.local_program_memory import LocalProgramMemory
import hybridagi.core.graph_program as gp

def test_local_program_memory_empty():
    program_memory = LocalProgramMemory(index_name="test")

def test_local_program_memory_update_one_prog():
    program_memory = LocalProgramMemory(index_name="test")
    
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
    
    assert program_memory._programs["main"] == main
    
def test_local_program_memory_remove_one_prog():
    program_memory = LocalProgramMemory(index_name="test")
    
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
    
    assert program_memory._programs["main"] == main
    program_memory.remove("main")
    assert len(program_memory._programs) == 0
    
def test_local_program_memory_update_dependencies_prog():
    program_memory = LocalProgramMemory(index_name="test")
    
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
    
    program_memory.update(clarify_objective)
    program_memory.update(main)

    assert program_memory.depends_on("main", "clarify_objective")