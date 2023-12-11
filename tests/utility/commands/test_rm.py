import unittest
from hybridagi import (
    Remove,
    FileSystemContext,
    FileSystem
)

from langchain.embeddings import FakeEmbeddings

class TestRemoveDirectory(unittest.TestCase):
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
        self.command = Remove(filesystem=self.filesystem)

    def test_remove_file(self):
        self.filesystem.create_document("/home/user/test_file.txt")
        self.command.execute(["/home/user/test_file.txt"], self.context)
        # Check if the file was removed
        self.assertFalse(self.filesystem.exists("/home/user/test_file.txt"))

    def test_remove_relative_file(self):
        self.filesystem.create_document("/home/user/test_file.txt")
        self.command.execute(["test_file.txt"], self.context)
        # Check if the file was removed
        self.assertFalse(self.filesystem.exists("/home/user/test_file.txt"))

    def test_remove_nonexistent_file(self):
        # Attempt to remove a nonexistent file
        result = self.command.execute(
            ["/home/user/nonexistent_file.txt"],
            self.context
        )
        # Check if the result contains the correct error message
        self.assertEqual(
            result,
            "Cannot remove /home/user/nonexistent_file.txt: No such file or directory"
        )

    def test_remove_empty_folder(self):
        self.filesystem.create_folder("/home/user/test_remove_empty_folder")
        self.assertTrue(
            self.command.filesystem.exists("/home/user/test_remove_empty_folder")
        )
        self.command.execute(
            ["/home/user/test_remove_empty_folder"],
            self.context
        )
        # Check if the folder was removed
        self.assertFalse(
            self.command.filesystem.exists("/home/user/test_remove_empty_folder")
        )

    def test_remove_nonempty_folder(self):
        self.filesystem.create_folder("/home/user/Tests")
        self.filesystem.create_document("/home/user/Tests/test_file.txt")
        self.command.execute(["/home/user/Tests"], self.context)
        # Attempt to remove the nonempty folder
        result = self.command.execute(["/home/user/Tests"], self.context)
        # Check if the result contains the correct error message
        self.assertEqual(
            result,
            "Cannot remove /home/user/Tests: Not empty directory"
        )

if __name__ == '__main__':
    unittest.main()
