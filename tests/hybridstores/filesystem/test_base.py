import unittest
from langchain.embeddings import FakeEmbeddings

from hybridagi import BaseFileSystem

class TestBaseFileSystem(unittest.TestCase):
    def setUp(self):
        # Initialize a Redis client and the RedisGraphHybridStore
        self.redis_url = "redis://localhost:6379"
        self.index_name = "test"
        self.verbose = False
        self.embeddings = FakeEmbeddings(size=512)
        self.embeddings_dim = 512
        # Set up the RedisGraphHybridStore
        self.filesystem = BaseFileSystem(
            redis_url = self.redis_url,
            index_name = self.index_name,
            embeddings = self.embeddings,
            embeddings_dim = self.embeddings_dim,
            verbose = self.verbose
        )
        self.filesystem.clear()

    def test_constructor(self):
        self.assertEqual(self.index_name, self.filesystem.index_name)
        self.assertEqual(self.embeddings, self.filesystem.embeddings)
        self.assertEqual(self.verbose, self.filesystem.verbose)

    def test_create_document(self):
        self.filesystem.create_document("/home/user/test.py")
        self.assertTrue(self.filesystem.exists("/home/user/test.py"))

    def test_create_folder(self):
        self.filesystem.create_folder("/home/user/test")
        self.assertTrue(self.filesystem.exists("/home/user/test"))
        self.assertTrue(self.filesystem.is_folder("/home/user/test"))

    def test_add_texts(self):
        text = "This is a content"
        self.filesystem.add_texts(texts = [text])

    def test_add_multiple_texts(self):
        text = "This is a content"
        text2 = "This is a second content"
        self.filesystem.add_texts(texts = [text, text2])

    def test_initialize(self):
        self.filesystem.clear()
        self.filesystem.initialize()
        self.assertTrue(self.filesystem.exists("/"))
        self.assertTrue(self.filesystem.exists("/home"))
        self.assertTrue(self.filesystem.exists("/home/user"))

