import pytest
from hybridagi import (
    FakeEmbeddings,
    ChangeDirectory,
    FileSystemContext,
    FileSystem,
    AgentState,
)

def test_change_directory_valid_path():
    emb = FakeEmbeddings(dim=250)
    memory = FileSystem(
        index_name = "test",
        embeddings = emb,
        wipe_on_start = True,
    )

    agent_state = AgentState()

    command = ChangeDirectory(filesystem=memory)
    result = command.execute(["/home"], agent_state.context)
    assert result == "Successfully changed working directory /home"

def test_change_directory_relative_path():
    emb = FakeEmbeddings(dim=250)
    memory = FileSystem(
        index_name = "test",
        embeddings = emb,
        wipe_on_start = True,
    )

    agent_state = AgentState()
    agent_state.context.working_directory = "/home/user/Workspace"
    command = ChangeDirectory(filesystem=memory)
    result = command.execute(["../Music"], agent_state.context)
    assert result == "Successfully changed working directory /home/user/Music"

def test_change_directory_nonexistent_path():
    emb = FakeEmbeddings(dim=250)
    memory = FileSystem(
        index_name = "test",
        embeddings = emb,
        wipe_on_start = True,
    )

    agent_state = AgentState()
    command = ChangeDirectory(filesystem=memory)
    with pytest.raises(ValueError) as e:
        result = command.execute(["/home/user/TestNonExistant"], agent_state.context)
    assert str(e.value) == "Cannot change directory /home/user/TestNonExistant: No such file or directory"

def test_change_directory_file_path():
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
    command = ChangeDirectory(filesystem=memory)
    with pytest.raises(ValueError) as e:
        result = command.execute(["/home/user/test_file.txt"], agent_state.context)
    assert str(e.value) == "Cannot change directory /home/user/test_file.txt: Not a directory"

def test_change_directory_no_input_path():
    emb = FakeEmbeddings(dim=250)
    memory = FileSystem(
        index_name = "test",
        embeddings = emb,
        wipe_on_start = True,
    )
    agent_state = AgentState()
    command = ChangeDirectory(filesystem=memory)
    with pytest.raises(ValueError) as e:
        result = command.execute([], agent_state.context)
    assert str(e.value) == "Cannot change directory: Input path not provided."



#     def test_change_directory_nonexistent_path(self):
#         self.filesystem.create_folder("/home/user/Workspace")
#         self.context.working_directory = "/home/user/Workspace"
#         with self.assertRaises(ValueError) as context:
#             self.command.execute(["/home/user/TestNonExistant"], self.context)
        
#         self.assertEqual(
#             str(context.exception),
#             "Cannot change directory /home/user/TestNonExistant: No such file or directory"
#         )
#         self.assertEqual(self.context.working_directory, "/home/user/Workspace")

#     def test_change_directory_file_path(self):
#         self.filesystem.create_folder("/home/user/Workspace")
#         self.context.working_directory = "/home/user/Workspace"
#         with self.assertRaises(ValueError) as context:
#             self.command.execute(["/home/user/test_file.txt"], self.context)
#         self.assertEqual(
#             str(context.exception),
#             "Cannot change directory /home/user/test_file.txt:"+\
#             " No such file or directory"
#         )
#         self.assertEqual(self.context.working_directory, "/home/user/Workspace")

#     def test_change_directory_no_input_path(self):
#         self.filesystem.create_folder("/home/user/Workspace")
#         self.context.working_directory = "/home/user/Workspace"
#         result = self.command.execute([], self.context)
#         self.assertEqual(result, "Cannot change directory: Input path not provided.")
#         self.assertEqual(self.context.working_directory, "/home/user/Workspace")

# if __name__ == '__main__':
#     unittest.main()
