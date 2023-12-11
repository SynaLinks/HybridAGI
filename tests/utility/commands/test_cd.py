import unittest
from hybridagi import (
    ChangeDirectory,
    FileSystemContext,
    FileSystem
)

from langchain.embeddings import FakeEmbeddings

class TestChangeDirectory(unittest.TestCase):
    def setUp(self):
        self.embeddings = FakeEmbeddings(size=512)
        self.embeddings_dim = 512
        self.context = FileSystemContext()
        self.filesystem = FileSystem(
            redis_url = 'redis://localhost:6379',
            index_name = 'test_index',
            embeddings = self.embeddings,
            embeddings_dim = self.embeddings_dim,
            context = self.context)
        self.filesystem.clear()
        self.filesystem.initialize()
        self.command = ChangeDirectory(filesystem=self.filesystem)

    def test_change_directory_valid_path(self):
        self.context.working_directory = "/home/user"
        result = self.command.execute(["/home"], self.context)
        self.assertEqual(
            result,
            "Successfully changed working directory /home"
        )
        self.assertEqual(self.context.working_directory, "/home")

    def test_change_directory_relative_path(self):
        self.context.working_directory = self.context.home_directory
        self.filesystem.create_folder("/home/user/Workspace")
        self.filesystem.create_folder("/home/user/Music")
        self.context.working_directory = "/home/user/Workspace"
        result = self.command.execute(["../Music"], self.context)
        self.assertEqual(
            result,
            "Successfully changed working directory /home/user/Music"
        )
        self.assertEqual(self.context.working_directory, "/home/user/Music")

    def test_change_directory_nonexistent_path(self):
        self.filesystem.create_folder("/home/user/Workspace")
        self.context.working_directory = "/home/user/Workspace"
        with self.assertRaises(ValueError) as context:
            self.command.execute(["/home/user/TestNonExistant"], self.context)
        
        self.assertEqual(
            str(context.exception),
            "Cannot change directory /home/user/TestNonExistant: No such file or directory"
        )
        self.assertEqual(self.context.working_directory, "/home/user/Workspace")

    def test_change_directory_file_path(self):
        self.filesystem.create_folder("/home/user/Workspace")
        self.context.working_directory = "/home/user/Workspace"
        with self.assertRaises(ValueError) as context:
            self.command.execute(["/home/user/test_file.txt"], self.context)
        self.assertEqual(
            str(context.exception),
            "Cannot change directory /home/user/test_file.txt:"+\
            " No such file or directory"
        )
        self.assertEqual(self.context.working_directory, "/home/user/Workspace")

    def test_change_directory_no_input_path(self):
        self.filesystem.create_folder("/home/user/Workspace")
        self.context.working_directory = "/home/user/Workspace"
        result = self.command.execute([], self.context)
        self.assertEqual(result, "Cannot change directory: Input path not provided.")
        self.assertEqual(self.context.working_directory, "/home/user/Workspace")

if __name__ == '__main__':
    unittest.main()
