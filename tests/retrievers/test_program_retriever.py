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
        index_name = "test",
        embeddings = emb,
    )
    assert retriever.forward("test").passages[0]["subprogram"] == "test_program: Test description"