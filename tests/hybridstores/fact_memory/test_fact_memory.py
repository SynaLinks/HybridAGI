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


def test_delete_triplet():
    emb = FakeEmbeddings(dim=250)
    memory = FactMemory(
        index_name="test",
        embeddings=emb,
        wipe_on_start=True,
    )

    memory.add_triplet("myself", "is a", "robot")
    memory.delete_triplet("myself", "is a", "robot")
    assert len(memory.get_triplets("myself")) == 0