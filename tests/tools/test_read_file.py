import unittest
from langchain_community.embeddings import FakeEmbeddings
from hybridagi import FileSystem
from hybridagi.tools import ReadFileTool

class TestAppendFileTool(unittest.TestCase):
    def setUp(self):
        self.redis_url = "redis://localhost:6379"
        self.index_name = "test"
        self.verbose = False
        self.embeddings = FakeEmbeddings(size=512)
        self.embeddings_dim = 512
        self.filesystem = FileSystem(
            redis_url = self.redis_url,
            index_name = self.index_name,
            embeddings = self.embeddings,
            embeddings_dim = self.embeddings_dim,
            verbose = self.verbose
        )
        self.filesystem.clear()
        self.filesystem.initialize()
        self.tool = ReadFileTool(filesystem = self.filesystem)

    def test_read_file(self):
        self.filesystem.add_documents(
            ["/home/user/hello_world.py"],
            ["""print("hello world 1")"""],
            languages=["python"]
        )
        self.filesystem.append_documents(
            ["/home/user/hello_world.py"],
            ["""print("hello world 2")"""],
            languages=["python"]
        )
        response = self.tool.run("/home/user/hello_world.py")
        self.assertEqual(response, 'print("hello world 1")\n\n[...]')
        response = self.tool.run("/home/user/hello_world.py")
        self.assertEqual(response, 'print("hello world 2")')