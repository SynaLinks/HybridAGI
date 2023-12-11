import unittest
from hybridagi import (
    PrintWorkingDirectory,
    FileSystemContext,
    FileSystem
)

from langchain.embeddings import FakeEmbeddings
    
class TestPrintWorkingDirectory(unittest.TestCase):
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
        self.command = PrintWorkingDirectory(filesystem=self.filesystem)

    def test_print_working_directory(self):
        # Execute the pwd command
        result = self.command.execute([], self.context)

        # The result should match the home directory path
        self.assertEqual(result, "/home/user")

    def test_print_working_directory_root(self):
        # Change the working directory
        self.context.working_directory = "/"
        # Execute the pwd command
        result = self.command.execute([], self.context)
        # The result should match the root directory path "/"
        self.assertEqual(result, "/")

if __name__ == '__main__':
    unittest.main()
