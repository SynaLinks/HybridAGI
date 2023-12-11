# import unittest
# from hybrid_agi import ProgramTraceMemory

# class TestProgramTraceMemory(unittest.TestCase):
#     def setUp(self):
#         self.memory = ProgramTraceMemory(chunk_size=10)
#         self.max_tokens = 400

#     def test_clear_program_trace(self):
#         self.memory.program_trace.append("Sample trace")
#         self.memory.clear()
#         self.assertEqual(len(self.memory.program_trace), 0)
    
#     def test_update_trace(self):
#         self.memory.update_trace("Prompt 1")
#         self.assertEqual(len(self.memory.program_trace), 1)
#         self.assertEqual(self.memory.program_trace[0], "Prompt 1")

#     def test_update_objective(self):
#         self.memory.update_objective("New Objective")
#         self.assertEqual(self.memory.objective, "New Objective")

#     def test_get_trace_single_chunk_not_truncated(self):
#         self.memory.program_trace.append("This is a single chunk of text.")
#         result = self.memory.get_trace(4000)
#         self.assertIn("Objective: ", result)
#         self.assertIn("This is a single chunk of text.", result)
    
#     def test_get_trace_single_chunk_truncated(self):
#         self.memory.program_trace.append("This is a single chunk of text.")
#         result = self.memory.get_trace(20)
#         self.assertIn("Objective: ", result)
#         self.assertIn("This is a single chunk of text.", result)


# if __name__ == "__main__":
#     unittest.main()