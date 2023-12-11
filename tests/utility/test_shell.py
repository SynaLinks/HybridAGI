import unittest
from typing import List

from hybridagi import (
    FileSystemContext,
    FileSystem,
    BaseShellCommand,
    ShellUtility
)

from langchain.embeddings import FakeEmbeddings

class FakeCommand(BaseShellCommand):

    def __init__(self, filesystem: FileSystem):
        super().__init__(
            filesystem,
            "mock",
            "mock a unix-like command")

    def execute(self, args: List[str], ctx: FileSystemContext) -> str:
        return "Mock command executed"

    def get_instructions(self) -> str:
        return "No Input needed"

class TestShellUtility(unittest.TestCase):

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
            context = self.context
        )
        self.filesystem.clear()

        # Register the mock command
        mock_command = FakeCommand(filesystem=self.filesystem)
        self.virtual_shell = ShellUtility(
            self.filesystem,
            commands=[mock_command]
        )

    def test_execute_supported_command(self):
        result = self.virtual_shell.execute(["mock"])
        self.assertEqual(result, "Mock command executed")

    def test_execute_unsupported_command(self):
        with self.assertRaises(ValueError) as context:
            self.virtual_shell.execute(["unsupported"])
        self.assertEqual(
            str(context.exception),
            "Command 'unsupported' not supported"
        )

    def test_execute_empty_command(self):
        with self.assertRaises(ValueError) as context:
            self.virtual_shell.execute([])
        expected_error = "Please use one of the following commands: ['mock']"
        self.assertEqual(str(context.exception), expected_error)

if __name__ == '__main__':
    unittest.main()
