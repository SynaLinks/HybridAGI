import unittest
from langchain.embeddings import FakeEmbeddings
from hybridagi import BaseHybridStore

class TestBaseHybridStore(unittest.TestCase):
    def setUp(self):
        # Initialize a Redis client and the RedisGraphHybridStore
        self.redis_url = "redis://localhost:6379"
        self.index_name = "test"
        self.verbose = False
        self.embeddings = FakeEmbeddings(size=512)
        self.embeddings_dim = 512
        # Set up the RedisGraphHybridStore
        self.hybridstore = BaseHybridStore(
            redis_url = self.redis_url,
            index_name = self.index_name,
            embeddings = self.embeddings,
            embeddings_dim = self.embeddings_dim,
            graph_index = "hybridstore",
            verbose = self.verbose)
        self.hybridstore.clear()

    def test_constructor(self):
        self.assertEqual(self.index_name, self.hybridstore.index_name)
        self.assertEqual(self.verbose, self.hybridstore.verbose)

    def test_create_graph(self):
        graph = self.hybridstore.create_graph("test_graph")
        self.assertEqual(graph.name, "test_graph")
        self.assertEqual(graph._graph.name, "test:graph:test_graph")
        self.assertEqual(graph.index_name, "test")
        
    def test_graph_query(self):
        graph = self.hybridstore.create_graph("test_graph")
        graph.query("RETURN 1")

    def test_set_content(self):
        text = "This is a content"
        self.assertTrue(self.hybridstore.set_content("test_index", text))
        self.assertTrue(self.hybridstore.exists("test_index"))

    def test_set_and_retreive_content(self):
        text = "This is a content"
        self.hybridstore.set_content("test_index", text)
        self.assertEqual(text, self.hybridstore.get_content("test_index"))

    def test_set_content_description(self):
        text = "This is a content"
        description = "This is a content description"
        self.hybridstore.set_content("test_index", text)
        self.assertTrue(self.hybridstore.set_content_description("test_index", description))

    def test_set_and_retreive_content_description(self):
        text = "This is a content"
        description = "This is a content description"
        self.hybridstore.set_content("test_index", text)
        self.hybridstore.set_content_description("test_index", description)
        self.assertEqual(description, self.hybridstore.get_content_description("test_index"))

    def test_set_content_metadata(self):
        text = "This is a content"
        metadata = {"metadata": "this is a content metadata"}
        self.hybridstore.set_content("test_index", text)
        self.assertTrue(self.hybridstore.set_content_metadata("test_index", metadata))

    def test_set_and_retreive_content_metadata(self):
        text = "This is a content"
        metadata = {"metadata": "this is a content metadata"}
        self.hybridstore.set_content("test_index", text)
        self.hybridstore.set_content_metadata("test_index", metadata)
        self.assertEquals(metadata, self.hybridstore.get_content_metadata("test_index"))

    def test_delete_content(self):
        text = "This is a content"
        self.hybridstore.set_content("test_index", text)
        self.hybridstore.delete_content("test_index")
        self.assertEqual(None, self.hybridstore.get_content("test_index"))