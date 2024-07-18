from hybridagi.memory.integration.local.local_program_memory import LocalProgramMemory
import hybridagi.core.graph_program as gp

def test_local_program_memory_empty():
    mem = LocalProgramMemory(index_name="test")

def test_local_program_memory_update_one_prog():
    mem = LocalProgramMemory(index_name="test")
    
    main = gp.GraphProgram(
        name="main",
        description="The main program",
    )
    
    main.add("answer", gp.Action(
        tool="Speak",
        purpose="Answer the given question",
        prompt="Please answer to the following question: {{question}}",
        inputs=["objective"],
    ))

    main.connect("start", "answer")
    main.connect("answer", "end")
    
    main.build()
    
    mem.update(main)
    
    assert mem._programs["main"] == main
    
    
def test_local_program_memory_remove_one_prog():
    mem = LocalProgramMemory(index_name="test")
    
    main = gp.GraphProgram(
        name="main",
        description="The main program",
    )
    
    main.add("answer", gp.Action(
        tool="Speak",
        purpose="Answer the given question",
        prompt="Please answer to the following question: {{question}}",
        inputs=["objective"],
    ))

    main.connect("start", "answer")
    main.connect("answer", "end")
    
    main.build()
    
    mem.update(main)
    
    assert mem._programs["main"] == main
    mem.remove("main")
    assert len(mem._programs) == 0
    
def test_local_program_memory_update_dependencies_prog():
    mem = LocalProgramMemory(index_name="test")
    
    clarify_objective = gp.GraphProgram(
        name="clarify_objective",
        description="Clarify the objective by asking question to the user",
    )

    clarify_objective.add("is_anything_unclear", gp.Decision(
        purpose = "Check if the question is unclear",
        prompt = "Is the following question '{{objective}}' still unclear?",
        inputs = ["objective"],
    ))

    clarify_objective.add("ask_question", gp.Action(
        purpose = "Ask question to clarify the user request",
        tool = "AskUser",
        prompt = "Pick one question to clarify the following user request: {{objective}}",
        inputs = ["objective"],
        output = "clarification",
    ))

    clarify_objective.add("refine_objective", gp.Action(
        purpose = "Refine the question",
        tool = "Predict",
        prompt = "Refine the following '{{question}}' based on the following clarification step: {{clarification}}",
        inputs = ["objective", "clarification"],
        output = "objective",
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

    main.add("clarify_objective", gp.Program(
        purpose = "Clarify the user objective if needed",
        prompt = "{{objective}}",
        inputs = ["objective"],
        program = "clarify_objective"
    ))

    main.add("answer", gp.Action(
        purpose = "Answer the objective's question",
        tool = "Speak",
        prompt = "Answer the following question: {{objective}}",
    ))

    main.connect("start", "clarify_objective")
    main.connect("clarify_objective", "answer")
    main.connect("answer", "end")

    main.build()
    
    mem.update(clarify_objective)
    mem.update(main)

    assert mem.depends_on("main", "clarify_objective")