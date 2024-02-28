import unittest
import numpy as np
from hybridagi import FileSystem
from hybridagi.tools import ContentSearchTool

from langchain_community.embeddings import GPT4AllEmbeddings

def _normalize_vector(value):
    return np.add(np.divide(value, 2), 0.5)

class TestContentSearchTool(unittest.TestCase):
    def setUp(self):
        self.redis_url = "redis://localhost:6379"
        self.index_name = "test"
        self.verbose = False
        self.embeddings = GPT4AllEmbeddings()
        self.embeddings_dim = 384
        self.filesystem = FileSystem(
            redis_url = self.redis_url,
            index_name = self.index_name,
            embeddings = self.embeddings,
            embeddings_dim = self.embeddings_dim,
            normalize = _normalize_vector,
            verbose = self.verbose)
        self.filesystem.clear()
        self.filesystem.initialize()
        self.tool = ContentSearchTool(filesystem = self.filesystem)

    def test_content_search(self):
        self.filesystem.clear()
        self.filesystem.initialize()
        self.filesystem.add_documents(
            paths=[
                "/home/user/test1.txt",
                "/home/user/test2.txt",
                "/home/user/test3.txt"
            ],
            texts=[
                """this is a test 1""",
                """this is a test 2""",
                """this is a test 3""",
            ],
            languages=[
                "plaintext",
                "plaintext",
                "plaintext"
            ]
        )
        input_string = "this is a test 1"
        result = self.tool.run(input_string)
        self.assertEqual(result, "this is a test 1")