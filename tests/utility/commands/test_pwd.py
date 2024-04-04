import pytest
from hybridagi import (
    FakeEmbeddings,
    PrintWorkingDirectory,
    FileSystemContext,
    FileSystem,
    AgentState,
)

def test_print_working_directory():
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

    command = PrintWorkingDirectory(filesystem=memory)
    result = command.execute([], agent_state.context)
    assert result == "/home/user"

def test_print_working_directory_root():
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
    agent_state.context.working_directory = "/"
    command = PrintWorkingDirectory(filesystem=memory)
    result = command.execute([], agent_state.context)
    assert result == "/"