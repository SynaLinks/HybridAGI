from hybridagi import ProgramMemory
from hybridagi import FakeEmbeddings

def test_add_one_program():
    emb = FakeEmbeddings(dim=250)
    memory = ProgramMemory(
        index_name="test",
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

    memory.add_texts(
        texts = [program],
        ids = [program_name]
    )
    assert memory.get_content(program_name) == program
    assert memory.get_content_description(program_name) == "Test description"

def test_add_programs_with_dependency():
    emb = FakeEmbeddings(dim=250)
    memory = ProgramMemory(
        index_name="test",
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

    memory.add_texts(
        texts = [program, subprogram],
        ids = [program_name, subprogram_name]
    )

    assert memory.get_content(program_name) == program
    assert memory.get_content(subprogram_name) == subprogram
    assert memory.exists(program_name, label='Program')
    assert memory.exists(subprogram_name, label='Program')
    assert memory.depends_on("program", "subprogram")

def test_load_folders():
    emb = FakeEmbeddings(dim=250)
    memory = ProgramMemory(
        index_name="test",
        embeddings=emb,
        wipe_on_start=True,
    )

    test_program = \
"""CREATE
(start:Control {name:'Start'}),
(end:Control {name:'End'}),
(start)-[:NEXT]->(end)"""

    memory.add_folders(
        ["tests/hybridstores/program_memory/test_folder"],
    )

    assert memory.exists("test_program", label='Program')
    assert memory.get_content("test_program") == test_program