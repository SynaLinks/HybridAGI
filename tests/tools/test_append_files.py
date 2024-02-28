import unittest
from langchain_community.embeddings import FakeEmbeddings
from hybridagi import FileSystem
from hybridagi.tools import AppendFilesTool

class TestAppendFilesTool(unittest.TestCase):
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
        self.tool = AppendFilesTool(filesystem = self.filesystem)

    def test_append_file(self):
        self.filesystem.add_documents(
            ["/home/user/hello_world.py"],
            ["""print("hello_world")"""],
            languages=["python"]
        )
        input_string = \
"""
hello_world.py
```python
print("hello world again!")
```
"""
        response = self.tool.run(input_string)
        result = self.filesystem.get_document("/home/user/hello_world.py")
        self.assertEqual(response, "Successfully modified 1 files")
        self.assertEqual(result, 'print("hello_world")\nprint("hello world again!")')

    def test_append_multiple_files(self):
        self.filesystem.add_documents(
            ["/home/user/hello_1.py", "/home/user/hello_2.py"],
            ["""print("hello_world")""", """print("hello_world")"""],
            languages=["python", "python"]
        )
        input_string = \
"""
hello_1.py
```python
print("hello world 1!")
```
hello_2.py
```python
print("hello world 2!")
```
"""
        self.tool.run(input_string)
        result = self.filesystem.get_document("/home/user/hello_1.py")
        self.assertEqual(result, """print("hello_world")\nprint("hello world 1!")""")
        result = self.filesystem.get_document("/home/user/hello_2.py")
        self.assertEqual(result, """print("hello_world")\nprint("hello world 2!")""")

    def test_append_file_invalid_format(self):
        input_string = \
"""
This is a test document of non valid format.
"""
        with self.assertRaises(ValueError):
            self.tool.run(input_string)

    def test_append_nonexistant(self):
        input_string = \
"""
hello_world_42.py
```python
print("hello world again!")
```
"""
        self.tool.run(input_string)
        result = self.filesystem.get_document("/home/user/hello_world_42.py")
        self.assertEqual(result, """print("hello world again!")""")

        
