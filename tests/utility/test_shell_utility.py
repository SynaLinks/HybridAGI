import pytest
from typing import List
from hybridagi import (
    FakeEmbeddings,
    AgentState,
    FileSystem,
    BaseShellCommand,
    FileSystemContext,
    ShellUtility,
)

class FakeCommand(BaseShellCommand):

    def __init__(self, filesystem: FileSystem):
        super().__init__(
            filesystem=filesystem,
            name="mock",
            description="mock a unix-like command",
        )

    def execute(self, args: List[str], ctx: FileSystemContext) -> str:
        return "Mock command executed"

    def get_instructions(self) -> str:
        return "No Input needed"

def test_shell_utility_valid_command():
    emb = FakeEmbeddings(dim=250)
    memory = FileSystem(
        index_name = "test",
        embeddings = emb,
        wipe_on_start = True,
    )

    agent_state = AgentState()

    mock_command = FakeCommand(filesystem=memory)

    internal_shell = ShellUtility(
        filesystem = memory,
        agent_state = agent_state,
        commands = [mock_command],
    )

    result = internal_shell.execute(["mock"])
    assert result == "Mock command executed"

def test_shell_utility_unsupported_command():
    emb = FakeEmbeddings(dim=250)
    memory = FileSystem(
        index_name = "test",
        embeddings = emb,
        wipe_on_start = True,
    )

    agent_state = AgentState()

    mock_command = FakeCommand(filesystem=memory)
    internal_shell = ShellUtility(
        filesystem = memory,
        agent_state = agent_state,
        commands = [mock_command],
    )
    with pytest.raises(ValueError) as e:
        result = internal_shell.execute(["unsupported"])
    
    assert str(e.value) == "Command 'unsupported' not supported"

def test_shell_utility_empty_command():
    emb = FakeEmbeddings(dim=250)
    memory = FileSystem(
        index_name = "test",
        embeddings = emb,
        wipe_on_start = True,
    )

    agent_state = AgentState()

    mock_command = FakeCommand(filesystem=memory)
    internal_shell = ShellUtility(
        filesystem = memory,
        agent_state = agent_state,
        commands = [mock_command],
    )

    with pytest.raises(ValueError) as e:
        result = internal_shell.execute([])
    assert str(e.value) == "Please use one of the following commands: ['mock']"
