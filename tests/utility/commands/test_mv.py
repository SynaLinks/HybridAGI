import unittest
from hybridagi import (
    Move,
    FileSystemContext,
    FileSystem
)

from langchain_community.embeddings import FakeEmbeddings

class TestMove(unittest.TestCase):
    def setUp(self):
        self.embeddings = FakeEmbeddings(size=512)
        self.embeddings_dim = 512
        # Set up the RedisGraphHybridStore and the VirtualFileSystem
        self.context = FileSystemContext()
        self.filesystem = FileSystem(
            redis_url = 'redis://localhost:6379',
            index_name = 'test_index',
            embeddings = self.embeddings,
            embeddings_dim = self.embeddings_dim,
            context = self.context)     
        self.filesystem.clear()
        self.filesystem.initialize()
        self.command = Move(filesystem=self.filesystem)
    
    def test_move_file_within_same_directory(self):
        self.filesystem.create_document("/home/user/test_file.txt")
        self.command.execute(
            ["/home/user/test_file.txt", "/home/user/renamed_file.txt"],
            self.context
        )
        # Check if the file was moved to the new destination
        self.assertFalse(self.filesystem.exists("/home/user/test_file.txt"))
        self.assertTrue(self.filesystem.exists("/home/user/renamed_file.txt"))

    def test_move_file_to_different_directory(self):
        self.filesystem.create_folder("/home/user/Workspace")
        self.filesystem.create_document("/home/user/test_file.txt")
        self.command.execute(
            ["/home/user/test_file.txt", "/home/user/Workspace/test_file.txt"],
            self.context)
        # Check if the file was moved to the new destination
        self.assertFalse(self.filesystem.exists("/home/user/test_file.txt"))
        self.assertTrue(self.filesystem.exists("/home/user/Workspace/test_file.txt"))

    def test_move_file_to_existing_destination(self):
        self.filesystem.create_document("/home/user/test_file.txt")
        with self.assertRaises(ValueError) as context:
            self.command.execute(
                ["/home/user/test_file.txt", "/home/user"],
                self.context)
        # Check if an error is raised when moving to an existing destination
        self.assertEqual(
            str(context.exception),
            "Cannot move: File or directory already exists")

    def test_move_nonexistent_file(self):
        # Attempt to move a nonexistent file
        self.context.working_directory = "/home/user"
        with self.assertRaises(ValueError) as context:
            self.command.execute(
                ["/home/user/nonexistent_file.txt", "/home/user/new_folder"],
                self.context)
        # Check if an error is raised when moving a nonexistent file
        self.assertEqual(
            str(context.exception),
            "Cannot move: /home/user/nonexistent_file.txt: No such file")

if __name__ == '__main__':
    unittest.main()
