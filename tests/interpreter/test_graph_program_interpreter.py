import unittest
from langchain_community.embeddings import FakeEmbeddings
from langchain_community.chat_models import FakeListChatModel
from langchain_core.messages import AIMessage

from hybridagi import ProgramMemory, TraceMemory
from hybridagi import GraphProgramInterpreter

class TestGraphProgramInterpreter(unittest.TestCase):
    def setUp(self):
        # Initialize a Redis client and the RedisGraphHybridStore
        self.redis_url = "redis://localhost:6379"
        self.index_name = "test"
        self.verbose = False
        self.embeddings = FakeEmbeddings(size=512)
        self.embeddings_dim = 512

        self.smart_llm = FakeListChatModel(
            responses=[
                AIMessage("hello"),
            ],
        )
        self.fast_llm = self.smart_llm
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

        self.trace_memory = TraceMemory(
            redis_url = self.redis_url,
            index_name = self.index_name,
            embeddings = self.embeddings,
            embeddings_dim = self.embeddings_dim,
            verbose = self.verbose,
        )
        self.trace_memory.clear()
        self.trace_memory.initialize()

        self.interpreter = GraphProgramInterpreter(
            program_memory = self.program_memory,
            trace_memory = self.trace_memory,
            fast_llm = self.fast_llm,
            smart_llm = self.smart_llm,
            verbose = self.verbose,
        )

    def test_call_program(self):
        program_name = "test_program"
        self.assertFalse(self.program_memory.exists(program_name))
        self.program_memory.add_programs(
            ["main.cypher", f"{program_name}.cypher"],
            ["CREATE (start:Control {name:'Start'}), (end:Control {name:'End'}), (start)-[:NEXT]->(end)",
             "CREATE (start:Control {name:'Start'}), (end:Control {name:'End'}), (start)-[:NEXT]->(end)",
            ],
        )
        self.assertTrue(self.program_memory.exists(program_name))
        self.assertTrue(self.program_memory.exists("main"))
        self.interpreter.start("Test")
        self.assertEqual(self.interpreter.call_program_tool(program_name), f"Successfully called '{program_name}' program")

    def test_call_nonexistant_program(self):
        self.program_memory.add_programs(
            ["main.cypher"],
            ["CREATE (start:Control {name:'Start'}), (end:Control {name:'End'}), (start)-[:NEXT]->(end)"],
        )
        program_name = "test_program_nonexistant"
        self.interpreter.start("Test")
        self.assertEqual(self.interpreter.call_program_tool(program_name), f"Error while calling '{program_name}': This program does not exist, verify its name")

    def test_call_protected_program(self):
        self.program_memory.add_programs(
            ["main.cypher"],
            ["CREATE (start:Control {name:'Start'}), (end:Control {name:'End'}), (start)-[:NEXT]->(end)"],
        )
        self.interpreter.start("main")
        self.assertEqual(self.interpreter.call_program_tool("main"), "Error while calling 'main': Trying to call a protected program")


if __name__ == "__main__":
    unittest.main()