from hybridagi import FileSystem
from hybridagi import FactMemory
from hybridagi import FakeEmbeddings

from hybridagi import KnowledgeLoader

from hybridagi import PythonKnowledgeParser
from hybridagi import TextKnowledgeParser

def test_knowledge_loader():
    emb = FakeEmbeddings(dim=250)
    filesystem = FileSystem(
        index_name = "test_loader",
        embeddings = emb,
        wipe_on_start = True,
    )
    fact_memory = FactMemory(
        index_name="test_loader",
        embeddings=emb,
        wipe_on_start=True,
    )

    parsers = [
        PythonKnowledgeParser(
            filesystem = filesystem,
            fact_memory = fact_memory,
        ),
        TextKnowledgeParser(
            filesystem = filesystem,
            fact_memory = fact_memory,
        ),
    ]

    loader = KnowledgeLoader(
        filesystem = filesystem,
        fact_memory = fact_memory,
        parsers = parsers,
    )

    loader.from_folders(["tests/loaders/test_data"])

    assert filesystem.is_folder("/home/user/test_data")
    assert filesystem.is_file("/home/user/test_data/program.py")
    assert filesystem.is_file("/home/user/test_data/text_file.txt")