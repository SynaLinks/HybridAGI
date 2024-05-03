from hybridagi import FactMemory
from hybridagi import FakeEmbeddings

def test_add_triplet():
    emb = FakeEmbeddings(dim=250)
    memory = FactMemory(
        index_name="test",
        embeddings=emb,
        wipe_on_start=True,
    )

    memory.add_triplet("myself", "is a", "robot")