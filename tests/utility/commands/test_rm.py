import pytest
from hybridagi import (
    FakeEmbeddings,
    Remove,
    FileSystemContext,
    FileSystem,
    AgentState,
)

def test_remove_file():
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
    memory.create_document("/home/user/test_file.txt")

    agent_state = AgentState()

    command = Remove(filesystem=memory)
    result = command.execute(["/home/user/test_file.txt"], agent_state.context)
    assert not memory.exists("/home/user/test_file.txt")

def test_remove_relative_file():
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
    memory.create_document("/home/user/test_file.txt")

    agent_state = AgentState()

    command = Remove(filesystem=memory)
    result = command.execute(["test_file.txt"], agent_state.context)
    assert not memory.exists("/home/user/test_file.txt")
    
def test_remove_nonexistent_file():
    emb = FakeEmbeddings(dim=250)
    memory = FileSystem(
        index_name = "test",
        embeddings = emb,
        wipe_on_start = True,
    )

    agent_state = AgentState()

    command = Remove(filesystem=memory)

    with pytest.raises(ValueError) as e:
        result = command.execute(["/home/user/nonexistent_file.txt"], agent_state.context)
    assert str(e.value) == "Cannot remove /home/user/nonexistent_file.txt: No such file or directory"

def test_remove_empty_folder():
    emb = FakeEmbeddings(dim=250)
    memory = FileSystem(
        index_name = "test",
        embeddings = emb,
        wipe_on_start = True,
    )

    agent_state = AgentState()

    command = Remove(filesystem=memory)

#     def test_remove_empty_folder(self):
#         self.filesystem.create_folder("/home/user/test_remove_empty_folder")
#         self.assertTrue(
#             self.command.filesystem.exists("/home/user/test_remove_empty_folder")
#         )
#         self.command.execute(
#             ["/home/user/test_remove_empty_folder"],
#             self.context
#         )
#         # Check if the folder was removed
#         self.assertFalse(
#             self.command.filesystem.exists("/home/user/test_remove_empty_folder")
#         )

#     def test_remove_nonempty_folder(self):
#         self.filesystem.create_folder("/home/user/Tests")
#         self.filesystem.create_document("/home/user/Tests/test_file.txt")
#         self.command.execute(["/home/user/Tests"], self.context)
#         # Attempt to remove the nonempty folder
#         result = self.command.execute(["/home/user/Tests"], self.context)
#         # Check if the result contains the correct error message
#         self.assertEqual(
#             result,
#             "Cannot remove /home/user/Tests: Not empty directory"
#         )

# if __name__ == '__main__':
#     unittest.main()
