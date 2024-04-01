from hybridagi import ProgramMemory
from hybridagi import FakeEmbeddings

def test_add_one_program():
    emb = FakeEmbeddings(dim=250)
    rm = ProgramMemory(
        index_name="test",
        graph_index="store",
        embeddings=emb,
        wipe_on_start=True,
    )
    program = \
"""
// @desc: Test description
CREATE
(start:Control {name:'Start'}),
(end:Control {name:'End'}),
(start)-[:NEXT]->(end)
"""
    program_name = "test_program"

    rm.add_texts(
        texts = [program],
        ids = [program_name]
    )
    assert rm.get_content(program_name) == program
    assert rm.get_content_description(program_name) == "Test description"

def test_add_programs_with_dependency():
    emb = FakeEmbeddings(dim=250)
    rm = ProgramMemory(
        index_name="test",
        graph_index="store",
        embeddings=emb,
        wipe_on_start=True,
    )
    program = \
"""
// @desc: Main program
CREATE
(start:Control {name:'Start'}),
(end:Control {name:'End'}),
(subprogram:Program {
    name:'Call a subprogram',
    program:'subprogram'}),
(start)-[:NEXT]->(subprogram),
(subprogram)-[:NEXT]->(end)
"""
    program_name = "program"

    subprogram = \
"""
// @desc: Subprogram
CREATE
(start:Control {name:'Start'}),
(end:Control {name:'End'}),
(start)-[:NEXT]->(end)
"""
    subprogram_name = "subprogram"

    rm.add_texts(
        texts = [program, subprogram],
        ids = [program_name, subprogram_name]
    )

    assert rm.get_content(program_name) == program
    assert rm.get_content(subprogram_name) == subprogram
    assert rm.exists(program_name, label='Program')
    assert rm.exists(subprogram_name, label='Program')
    assert rm.depends_on("program", "subprogram")