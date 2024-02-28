import unittest
from hybridagi import (
    MakeDirectory,
    FileSystemContext,
    FileSystem
)

from langchain_community.embeddings import FakeEmbeddings

class TestMakeDirectory(unittest.TestCase):
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
        self.command = MakeDirectory(filesystem=self.filesystem)

    def test_make_directory_valid_path(self):
        # Execute mkdir command to create a new directory
        result = self.command.execute(
            ["/home/user/test_make_directory"],
            self.context
        )

        # The result should confirm the successful creation of the directory
        self.assertEqual(
            result,
            "Sucessfully created directory /home/user/test_make_directory"
        )

        # Check if the directory actually exists in the virtual file system
        self.assertTrue(
            self.filesystem.exists("/home/user/test_make_directory")
        )

    def test_make_directory_multiple_path(self):
        # Execute mkdir command to create a new directories
        result = self.command.execute(
            ["/home/user/test_make_directory_1 /home/user/test_make_directory_2"],
            self.context
        )

        # The result should confirm the successful creation of the directory
        self.assertEqual(
            result,
            "Sucessfully created 2 directories"
        )
        # Check if the directory actually exists in the virtual file system
        self.assertTrue(
            self.filesystem.exists("/home/user/test_make_directory_1")
        )
        # Check if the directory actually exists in the virtual file system
        self.assertTrue(
            self.filesystem.exists("/home/user/test_make_directory_2")
        )

    def test_make_directory_relative_path(self):
        # Execute mkdir command with a relative path to create a new directory
        result = self.command.execute(
            ["test_make_directory_relative"],
            self.context
        )

        # The result should confirm the successful creation of the directory
        self.assertEqual(
            result,
            "Sucessfully created directory"+\
            " /home/user/test_make_directory_relative"
        )

        # Check if the directory actually exists in the virtual file system
        self.assertTrue(
            self.filesystem.exists("/home/user/test_make_directory_relative")
        )

    def test_make_directory_nonexistent_parent_directory(self):
        # Execute mkdir command to create
        # a new directory with a nonexistent parent directory
        with self.assertRaises(ValueError) as context:
            self.command.execute(["/dir/nonexistent_folder"], self.context)

        self.assertEqual(
            str(context.exception),
            "Cannot create directory /dir/nonexistent_folder:"+
            " '/dir' No such file or directory"
        )

        # Check if the parent directory was not created
        self.assertFalse(self.filesystem.exists("/home/nonexistent_folder"))

    def test_make_existing_directory(self):
        # Create a new directory
        self.filesystem.create_folder("/home/user/test_existing_directory")

        # Execute mkdir command to create a directory that already exists
        with self.assertRaises(ValueError) as context:
            self.command.execute(["test_existing_directory"], self.context)

        self.assertEqual(
            str(context.exception),
            "Cannot create directory "+\
            "/home/user/test_existing_directory: File exists"
        )

    def test_make_directory_no_input_path(self):
        # Execute mkdir command without providing the path
        with self.assertRaises(ValueError) as context:
            self.command.execute([], self.context)

        self.assertEqual(
            str(context.exception),
            "Cannot create directory: Missing operand."+\
            " Try 'mkdir --help' for more information."
        )

if __name__ == '__main__':
    unittest.main()
