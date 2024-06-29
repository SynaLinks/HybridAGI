from hybridagi import ProgramMemory
from hybridagi import FakeEmbeddings
from hybridagi import GraphProgramsLoader

def test_graph_programs_loader():
    emb = FakeEmbeddings(dim=250)
    program_memory = ProgramMemory(
        index_name = "test_loader",
        embeddings = emb,
        wipe_on_start = True,
    )

    loader = GraphProgramsLoader(
        program_memory = program_memory,
    )

    loader.from_folders(["tests/loaders/test_data"])

    assert program_memory.exists("main")