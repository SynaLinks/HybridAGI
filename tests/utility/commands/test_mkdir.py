import pytest
from hybridagi import (
    FakeEmbeddings,
    MakeDirectory,
    FileSystemContext,
    FileSystem,
    AgentState,
)

def test_make_directory_valid_path():
    emb = FakeEmbeddings(dim=250)
    memory = FileSystem(
        index_name = "test",
        embeddings = emb,
        wipe_on_start = True,
    )

    agent_state = AgentState()

    command = MakeDirectory(filesystem=memory)
    result = command.execute(["/home/user/test_make_directory"], agent_state.context)
    assert result == "Sucessfully created directory /home/user/test_make_directory"
    assert memory.exists("/home/user/test_make_directory")

def test_make_directory_multiple_path():
    emb = FakeEmbeddings(dim=250)
    memory = FileSystem(
        index_name = "test",
        embeddings = emb,
        wipe_on_start = True,
    )

    agent_state = AgentState()

    command = MakeDirectory(filesystem=memory)
    result = command.execute(["/home/user/test_make_directory_1 /home/user/test_make_directory_2"], agent_state.context)
    assert result == "Sucessfully created 2 directories"
    assert memory.exists("/home/user/test_make_directory_1")
    assert memory.exists("/home/user/test_make_directory_2")

def test_make_directory_relative_path():
    emb = FakeEmbeddings(dim=250)
    memory = FileSystem(
        index_name = "test",
        embeddings = emb,
        wipe_on_start = True,
    )

    agent_state = AgentState()

    command = MakeDirectory(filesystem=memory)
    result = command.execute(["test_make_directory"], agent_state.context)
    assert result == "Sucessfully created directory /home/user/test_make_directory"
    assert memory.exists("/home/user/test_make_directory")

def test_make_directory_nonexistent_parent_directory():
    emb = FakeEmbeddings(dim=250)
    memory = FileSystem(
        index_name = "test",
        embeddings = emb,
        wipe_on_start = True,
    )

    agent_state = AgentState()

    command = MakeDirectory(filesystem=memory)
    with pytest.raises(ValueError) as e:
        result = command.execute(["/dir/nonexistent_folder"], agent_state.context)
    assert str(e.value) == "Cannot create directory /dir/nonexistent_folder: '/dir' No such file or directory"

def test_make_existing_directory():
    emb = FakeEmbeddings(dim=250)
    memory = FileSystem(
        index_name = "test",
        embeddings = emb,
        wipe_on_start = True,
    )

    agent_state = AgentState()

    command = MakeDirectory(filesystem=memory)
    with pytest.raises(ValueError) as e:
        result = command.execute(["/home/user"], agent_state.context)
    assert str(e.value) == "Cannot create directory /home/user: File exists"

def test_make_directory_no_input_path():
    emb = FakeEmbeddings(dim=250)
    memory = FileSystem(
        index_name = "test",
        embeddings = emb,
        wipe_on_start = True,
    )

    agent_state = AgentState()

    command = MakeDirectory(filesystem=memory)
    with pytest.raises(ValueError) as e:
        result = command.execute([], agent_state.context)
    assert str(e.value) == "Cannot create directory: Missing operand. Try `mkdir --help` for more information."