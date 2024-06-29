# from hybridagi import FactMemory
# from hybridagi import FakeEmbeddings
# from hybridagi import PythonKnowledgeParser

# def test_python_parser():
#     emb = FakeEmbeddings(dim=250)
#     memory = FactMemory(
#         index_name="test",
#         embeddings=emb,
#         wipe_on_start=True,
#     )

#     parser = PythonKnowledgeParser(
#         fact_memory = memory,
#     )

#     parser.parse(filename="test.py", code=\
# """
# class HelloClass2(object, Base):

# 	def hello2(self):
#         print("hello")

# 	def say_hello2(self):
# 		pass

# def func_test():
#     pass

# class TestClass():
#     def __init__(self):
#         pass

# class HelloClass(object, Base):

# 	def hello(self):
#         print("hello")

# 	def say_hello(self):
# 		pass
# """
#     )

# def test_code_parser_with_large_project():
#     emb = FakeEmbeddings(dim=250)
#     memory = FactMemory(
#         index_name="test",
#         embeddings=emb,
#         wipe_on_start=True,
#     )

#     parser = PythonKnowledgeParser(
#         fact_memory = memory,
#     )
    
#     parser.add_folders(["hybridagi/"])