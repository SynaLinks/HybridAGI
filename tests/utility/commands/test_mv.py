import pytest
from hybridagi import (
    FakeEmbeddings,
    Move,
    FileSystemContext,
    FileSystem,
    AgentState,
)

def test_move_file_within_same_directory():
    emb = FakeEmbeddings(dim=250)
    memory = FileSystem(
        index_name = "test",
        embeddings = emb,
        wipe_on_start = True,
    )

    memory.add_texts(
        texts=["test text"],
        ids=["/home/user/test_file.txt"],
    )

    agent_state = AgentState()

    command = Move(filesystem=memory)
    result = command.execute(["/home/user/test_file.txt", "/home/user/renamed_file.txt"], agent_state.context)
    assert result == "Sucessfully moved"
    assert not memory.exists("/home/user/test_file.txt")
    assert memory.exists("/home/user/renamed_file.txt")
    assert memory.get_document("/home/user/renamed_file.txt") == "test text"

def test_move_file_to_different_directory():
    emb = FakeEmbeddings(dim=250)
    memory = FileSystem(
        index_name = "test",
        embeddings = emb,
        wipe_on_start = True,
    )

    memory.add_texts(
        texts=["test text"],
        ids=["/home/user/test_file.txt"],
    )

    agent_state = AgentState()

    command = Move(filesystem=memory)
    result = command.execute(["/home/user/test_file.txt", "/home/user/Workspace/test_file.txt"], agent_state.context)
    assert result == "Sucessfully moved"
    assert not memory.exists("/home/user/test_file.txt")
    assert memory.exists("/home/user/Workspace/test_file.txt")
    assert memory.get_document("/home/user/Workspace/test_file.txt") == "test text"

def test_move_file_to_existing_destination():
    emb = FakeEmbeddings(dim=250)
    memory = FileSystem(
        index_name = "test",
        embeddings = emb,
        wipe_on_start = True,
    )

    agent_state = AgentState()

    command = Move(filesystem=memory)
    memory.create_document("/home/user/test_file.txt")

    with pytest.raises(ValueError) as e:
        result = command.execute(["/home/user/test_file.txt", "/home/user"], agent_state.context)
    assert str(e.value) == "Cannot move: File or directory already exists"


def test_move_nonexistent_file():
    emb = FakeEmbeddings(dim=250)
    memory = FileSystem(
        index_name = "test",
        embeddings = emb,
        wipe_on_start = True,
    )

    agent_state = AgentState()

    command = Move(filesystem=memory)

    with pytest.raises(ValueError) as e:
        result = command.execute(["/home/user/test_file.txt", "/home/user"], agent_state.context)
    assert str(e.value) == "Cannot move: No such file"