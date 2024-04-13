import dspy
import pytest
from hybridagi import GraphProgramInterpreter
from hybridagi import ProgramMemory
from hybridagi import FakeEmbeddings

from hybridagi.tools import PredictTool
from dspy.utils.dummies import DummyLM

def test_no_program():
    emb = FakeEmbeddings(dim=250)

    answers = []

    dspy.settings.configure(lm=DummyLM(answers=answers))

    program_memory = ProgramMemory(
        index_name="test",
        embeddings = emb,
        wipe_on_start = True,
    )
    program_memory.clear()

    with pytest.raises(RuntimeError) as exc_info:
        _ = GraphProgramInterpreter(
            program_memory = program_memory,
            tools = [],
        )(objective="test")
    assert str(exc_info.value) == "No entry point detected, please make sure you loaded the programs."

def test_empty_program():
    emb = FakeEmbeddings(dim=250)

    answers = []

    dspy.settings.configure(lm=DummyLM(answers=answers))

    program_memory = ProgramMemory(
        index_name="test",
        embeddings=emb,
        wipe_on_start=True,
    )
    program = \
"""
// @desc: Test description
CREATE
(start:Control {name:"Start"}),
(end:Control {name:"End"}),
(start)-[:NEXT]->(end)
"""
    program_name = "main"

    program_memory.add_texts(
        texts = [program],
        ids = [program_name]
    )

    result = GraphProgramInterpreter(
        program_memory = program_memory,
        tools = [],
    )(objective="test")

    assert result.finish_reason == "finished"
    assert result.program_trace == \
""" --- Step 0 ---
Call Program: main
Program Purpose: test
 --- Step 1 ---
End Program: main"""

def test_one_action_program():

    emb = FakeEmbeddings(dim=250)

    answers = ["Toulouse"]

    dspy.settings.configure(lm=DummyLM(answers=answers))

    program_memory = ProgramMemory(
        index_name="test",
        embeddings=emb,
        wipe_on_start=True,
    )
    program = \
"""
// @desc: Answer the objective
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

    program_memory.add_texts(
        texts = [program],
        ids = [program_name]
    )

    tools = [
        PredictTool()
    ]

    result = GraphProgramInterpreter(
        program_memory = program_memory,
        tools = tools,
    )(objective = "What is the city of the spatial & robotics industry in France?")
    print(result.program_trace)
    assert result.finish_reason == "finished"
    assert result.program_trace == \
""" --- Step 0 ---
Call Program: main
Program Purpose: What is the city of the spatial & robotics industry in France?
 --- Step 1 ---
Action Purpose: Answer the objective's question
Action: {
  "answer": "Toulouse"
}
 --- Step 2 ---
End Program: main"""

def test_one_decision_program():
    emb = FakeEmbeddings(dim=250)

    answers = [
""" answer, the objective contains the character `?` denoting a question.\n\nAnswer: <YES>
"""
]

    dspy.settings.configure(lm=DummyLM(answers=answers))

    program_memory = ProgramMemory(
        index_name="test",
        embeddings=emb,
        wipe_on_start=True,
    )
    program = \
"""
// @desc: Answer the objective
CREATE
(start:Control {name:"Start"}),
(check_question:Decision {
    name: "Check if the objective is a question",
    question: "Is the objective a question?"
}),
(end:Control {name:"End"}),
(start)-[:NEXT]->(check_question),
(check_question)-[:YES]->(end),
(check_question)-[:NO]->(end)
"""
    program_name = "main"

    program_memory.add_texts(
        texts = [program],
        ids = [program_name]
    )

    tools = [
        PredictTool()
    ]

    result = GraphProgramInterpreter(
        program_memory = program_memory,
        tools = tools,
    )(objective = "What is the city of the spatial & robotics industry in France?")

    assert result.finish_reason == "finished"
    print(result.program_trace)
    assert result.program_trace == \
""" --- Step 0 ---
Call Program: main
Program Purpose: What is the city of the spatial & robotics industry in France?
 --- Step 1 ---
Decision Purpose: Check if the objective is a question
Decision Question: Is the objective a question?
Decision: YES
 --- Step 2 ---
End Program: main"""

def test_one_subprogram():
    emb = FakeEmbeddings(dim=250)

    answers = []

    dspy.settings.configure(lm=DummyLM(answers=answers))

    program_memory = ProgramMemory(
        index_name="test",
        embeddings=emb,
        wipe_on_start=True,
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

    program_memory.add_texts(
        texts = [program, subprogram],
        ids = [program_name, subprogram_name]
    )

    tools = [
        PredictTool()
    ]

    result = GraphProgramInterpreter(
        program_memory = program_memory,
        tools = tools,
    )(objective = "What is the city of the spatial & robotics industry in France?")

    assert result.finish_reason == "finished"
    assert result.program_trace == \
""" --- Step 0 ---
Call Program: main
Program Purpose: What is the city of the spatial & robotics industry in France?
 --- Step 1 ---
Call Program: subprogram
Program Purpose: Call a subprogram
 --- Step 2 ---
End Program: subprogram
 --- Step 3 ---
End Program: main"""


def test_multi_step_program():
    emb = FakeEmbeddings(dim=250)

    answers = [" answer, the objective contains the character `?` denoting a question.\n\nAnswer:YES", "Toulouse"]

    dspy.settings.configure(lm=DummyLM(answers=answers))

    program_memory = ProgramMemory(
        index_name="test",
        embeddings=emb,
        wipe_on_start=True,
    )
    program = \
"""
// @desc: Answer the objective
CREATE
(start:Control {name:"Start"}),
(check_objective:Decision {
    name: "Check if the objective is a question",
    question: "Is the objective a question?"
}),
(answer:Action {
    name: "Answer the objective's question",
    tool: "Predict",
    prompt: "You are an helpfull assistant, please answer the objective's question"
}),
(end:Control {name:"End"}),
(start)-[:NEXT]->(check_objective),
(check_objective)-[:YES]->(answer),
(check_objective)-[:NO]->(end),
(answer)-[:NEXT]->(end)
"""
    program_name = "main"

    program_memory.add_texts(
        texts = [program],
        ids = [program_name],
    )

    tools = [
        PredictTool()
    ]

    result = GraphProgramInterpreter(
        program_memory = program_memory,
        tools = tools,
    )(objective = "What is the city of the spatial & robotics industry in France?")

    assert result.finish_reason == "finished"
    assert result.program_trace == \
""" --- Step 0 ---
Call Program: main
Program Purpose: What is the city of the spatial & robotics industry in France?
 --- Step 1 ---
Decision Purpose: Check if the objective is a question
Decision Question: Is the objective a question?
Decision: YES
 --- Step 2 ---
Action Purpose: Answer the objective's question
Action: {
  "answer": "Toulouse"
}
 --- Step 3 ---
End Program: main"""