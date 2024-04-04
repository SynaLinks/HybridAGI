import pytest
from hybridagi import (
    FakeEmbeddings,
    Tree,
    FileSystemContext,
    FileSystem,
    AgentState,
)

def test_tree_home():
    emb = FakeEmbeddings(dim=250)
    memory = FileSystem(
        index_name = "test",
        embeddings = emb,
        wipe_on_start = True,
    )

    agent_state = AgentState()

    expected_output = \
"""/home/user
├── Documents
├── Downloads
├── Music
└── Pictures
4 directories, 0 files"""

    command = Tree(filesystem=memory)
    result = command.execute(["/home/user/"], agent_state.context)
    assert result == expected_output

def test_tree_root_path():
    emb = FakeEmbeddings(dim=250)
    memory = FileSystem(
        index_name = "test",
        embeddings = emb,
        wipe_on_start = True,
    )

    agent_state = AgentState()

    expected_output = \
"""/
└── home
    └── user
        ├── Documents
        ├── Downloads
        ├── Music
        └── Pictures
6 directories, 0 files"""

    command = Tree(filesystem=memory)
    result = command.execute(["/"], agent_state.context)
    assert result == expected_output

def test_tree_with_documents():
    emb = FakeEmbeddings(dim=250)
    memory = FileSystem(
        index_name = "test",
        embeddings = emb,
        wipe_on_start = True,
    )
    memory.create_document("/home/user/Documents/test_doc.txt")

    agent_state = AgentState()

    expected_output = \
"""/
└── home
    └── user
        ├── Documents
        │   └── test_doc.txt
        ├── Downloads
        ├── Music
        └── Pictures
6 directories, 1 files"""

    command = Tree(filesystem=memory)
    result = command.execute(["/"], agent_state.context)
    assert result == expected_output