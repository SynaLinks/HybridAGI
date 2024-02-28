import unittest
from hybridagi import (
    ListDirectory,
    FileSystemContext,
    FileSystem
)

from langchain_community.embeddings import FakeEmbeddings

class TestListDirectory(unittest.TestCase):
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
        self.command = ListDirectory(filesystem=self.filesystem)

    def test_list_directory_valid_path(self):
        # Create some folders and documents for testing
        self.filesystem.create_folder("/home/user/Tests/test_folder")
        self.filesystem.create_folder("/home/user/Tests/test_folder/sub_folder")
        self.filesystem.create_document("/home/user/Tests/test_folder/test_doc1.txt")
        self.filesystem.create_document("/home/user/Tests/test_folder/test_doc2.txt")
        # Execute ls command on the test_folder
        result = self.command.execute(["/home/user/Tests/test_folder"], self.context)

        # The result should contain the names of the 
        # sub_folder, test_doc1.txt, and test_doc2.txt
        self.assertIn("sub_folder", result)
        self.assertIn("test_doc1.txt", result)
        self.assertIn("test_doc2.txt", result)

    def test_list_directory_relative_path(self):
        # Create some folders and documents for testing
        self.filesystem.create_folder("/home/user/Tests/test_folder")
        self.filesystem.create_folder("/home/user/Tests/test_folder/sub_folder")
        self.filesystem.create_document("/home/user/Tests/test_folder/test_doc1.txt")
        self.filesystem.create_document("/home/user/Tests/test_folder/test_doc2.txt")     
        # Execute ls command with a relative path
        result = self.command.execute(["Tests/test_folder"], self.context)

        # The result should contain the names of the
        # sub_folder, test_doc1.txt, and test_doc2.txt
        self.assertIn("sub_folder", result)
        self.assertIn("test_doc1.txt", result)
        self.assertIn("test_doc2.txt", result)

    def test_list_nonexistent_directory(self):
        # Execute ls command on a nonexistent directory
        with self.assertRaises(ValueError) as context:
            self.command.execute(["nonexistent_folder"], self.context)

        self.assertEqual(
            str(context.exception),
            "Cannot list /home/user/nonexistent_folder: No such file or directory"
        )

    def test_list_file_as_directory(self):
        # Create some folders and documents for testing
        self.filesystem.create_folder("/home/user/Tests/test_folder")
        self.filesystem.create_folder("/home/user/Tests/test_folder/sub_folder")
        self.filesystem.create_document("/home/user/Tests/test_folder/test_doc1.txt")
        self.filesystem.create_document("/home/user/Tests/test_folder/test_doc2.txt")     
        # Execute ls command on a file path
        with self.assertRaises(ValueError) as context:
            self.command.execute(
                ["/home/user/Tests/test_folder/test_doc1.txt"],
                self.context
            )

        self.assertEqual(
            str(context.exception),
            "Cannot list /home/user/Tests/test_folder/test_doc1.txt: Not a directory"
        )

if __name__ == '__main__':
    unittest.main()
