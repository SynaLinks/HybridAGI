from hybridagi import ProgramMemory
from hybridagi import FakeEmbeddings
from hybridagi import ProgramRetriever

def test_forward():
    emb = FakeEmbeddings(dim=250)
    memory = ProgramMemory(
        index_name = "test",
        embeddings = emb,
        wipe_on_start=True,
    )
    program = \
"""
// @desc: Test description
CREATE
(start:Control {name:'Start'}),
(ensd:Control {name:'End'}),
(start)-[:NEXT]->(end)
"""
    program_name = "test_program"

    memory.add_texts(
        texts = [program],
        ids = [program_name]
    )

    retriever = ProgramRetriever(
        program_memory = memory,
        embeddings = emb,
        distance_threshold = 100.0,
    )
    assert retriever.forward("test").routines[0]["routine"] == "test_program: Test description"

def test_forward_multiple():
    emb = FakeEmbeddings(dim=250)
    memory = ProgramMemory(
        index_name = "test",
        embeddings = emb,
        wipe_on_start=True,
    )

    program1 = \
"""
// @desc: Test description one
CREATE
(start:Control {name:'Start'}),
(ensd:Control {name:'End'}),
(start)-[:NEXT]->(end)
"""

    program2 = \
"""
// @desc: Test description two
CREATE
(start:Control {name:'Start'}),
(ensd:Control {name:'End'}),
(start)-[:NEXT]->(end)
"""
    program_name = "test_program"
    
    memory.add_texts(
        texts = [program1, program2],
        ids = ["test_program1", "test_program2"]
    )

    retriever = ProgramRetriever(
        program_memory = memory,
        embeddings = emb,
        distance_threshold = 100.0,
    )

    assert len(retriever.forward(["test"]).routines) == 2