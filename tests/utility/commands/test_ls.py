import pytest
from hybridagi import (
    FakeEmbeddings,
    ListDirectory,
    FileSystemContext,
    FileSystem,
    AgentState,
)

def test_list_directory_valid_path():
    emb = FakeEmbeddings(dim=250)
    memory = FileSystem(
        index_name = "test",
        embeddings = emb,
        wipe_on_start = True,
    )
    memory.create_folder("/home/user/Tests")
    memory.create_folder("/home/user/Tests/test_folder")
    memory.create_folder("/home/user/Tests/test_folder/sub_folder")
    memory.create_document("/home/user/Tests/test_folder/test_doc1.txt")
    memory.create_document("/home/user/Tests/test_folder/test_doc2.txt")

    agent_state = AgentState()

    command = ListDirectory(filesystem=memory)
    result = command.execute(["/home/user/Tests/test_folder"], agent_state.context)
    assert "sub_folder" in result
    assert "test_doc1.txt" in result
    assert "test_doc2.txt" in result

def test_list_directory_relative_path():
    emb = FakeEmbeddings(dim=250)
    memory = FileSystem(
        index_name = "test",
        embeddings = emb,
        wipe_on_start = True,
    )
    memory.create_folder("/home/user/Tests")
    memory.create_folder("/home/user/Tests/test_folder")
    memory.create_folder("/home/user/Tests/test_folder/sub_folder")
    memory.create_document("/home/user/Tests/test_folder/test_doc1.txt")
    memory.create_document("/home/user/Tests/test_folder/test_doc2.txt")

    agent_state = AgentState()

    command = ListDirectory(filesystem=memory)
    result = command.execute(["Tests/test_folder"], agent_state.context)
    assert "sub_folder" in result
    assert "test_doc1.txt" in result
    assert "test_doc2.txt" in result

def test_list_nonexistent_directory():
    emb = FakeEmbeddings(dim=250)
    memory = FileSystem(
        index_name = "test",
        embeddings = emb,
        wipe_on_start = True,
    )

    agent_state = AgentState()

    command = ListDirectory(filesystem=memory)

    with pytest.raises(ValueError) as e:
        result = command.execute(["nonexistent_folder"], agent_state.context)
    assert str(e.value) == "Cannot list /home/user/nonexistent_folder: No such file or directory"

def test_list_file_not_directory():
    emb = FakeEmbeddings(dim=250)
    memory = FileSystem(
        index_name = "test",
        embeddings = emb,
        wipe_on_start = True,
    )
    memory.create_folder("/home/user/Tests")
    memory.create_folder("/home/user/Tests/test_folder")
    memory.create_folder("/home/user/Tests/test_folder/sub_folder")
    memory.create_document("/home/user/Tests/test_folder/test_doc1.txt")
    memory.create_document("/home/user/Tests/test_folder/test_doc2.txt")

    agent_state = AgentState()

    command = ListDirectory(filesystem=memory)

    with pytest.raises(ValueError) as e:
        result = command.execute(["/home/user/Tests/test_folder/test_doc1.txt"], agent_state.context)
    assert str(e.value) == "Cannot list /home/user/Tests/test_folder/test_doc1.txt: Not a directory"
