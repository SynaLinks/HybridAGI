import unittest
from langchain_community.embeddings import FakeEmbeddings

from hybridagi import ProgramMemory

class TestProgramMemory(unittest.TestCase):
    def setUp(self):
        # Initialize a Redis client and the RedisGraphHybridStore
        self.redis_url = "redis://localhost:6379"
        self.index_name = "test"
        self.verbose = False
        self.embeddings = FakeEmbeddings(size=512)
        self.embeddings_dim = 512
        # Set up the RedisGraphHybridStore
        self.program_memory = ProgramMemory(
            redis_url = self.redis_url,
            index_name = self.index_name,
            embeddings = self.embeddings,
            embeddings_dim = self.embeddings_dim,
            verbose = self.verbose
        )
        self.program_memory.clear()
        self.program_memory.initialize()

    def test_add_program(self):
        self.assertFalse(self.program_memory.exists("test_program"))
        self.program_memory.add_programs(
            ["test_program.cypher"],
            ["CREATE (start:Control {name:'Start'}), (end:Control {name:'End'}), (start)-[:NEXT]->(end)"],
        )
        self.assertTrue(self.program_memory.exists("test_program"))

    def test_add_folder(self):
        self.program_memory.load_folders(
            ["tests/hybridstores/program_memory/test_folder"],
        )
        self.assertTrue(self.program_memory.exists("test_program_1"))
        self.assertTrue(self.program_memory.exists("test_program_2"))


if __name__ == "__main__":
    unittest.main()