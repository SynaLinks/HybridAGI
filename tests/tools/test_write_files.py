import unittest
from langchain_community.embeddings import FakeEmbeddings
from hybridagi import FileSystem
from hybridagi.tools import WriteFilesTool

class TestWriteFilesTool(unittest.TestCase):
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
        self.tool = WriteFilesTool(filesystem = self.filesystem)

    def test_write_file(self):
        input_string = \
"""
hello_world.py
```python
print("hello world")
```
"""
        response = self.tool.run(input_string)
        result = self.filesystem.get_document("/home/user/hello_world.py")
        self.assertEqual(response, "Successfully created 1 files")
        self.assertEqual(result, """print("hello world")""")

    def test_write_multiple_files(self):
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
        res = self.tool.run(input_string)
        self.assertEqual(res, "Successfully created 2 files")
        result = self.filesystem.get_document("/home/user/hello_1.py")
        self.assertEqual(result, """print("hello world 1!")""")
        result = self.filesystem.get_document("/home/user/hello_2.py")
        self.assertEqual(result, """print("hello world 2!")""")

    def test_write_file_invalid_format(self):
        input_string = \
"""
This is a test document of non valid format.
"""
        with self.assertRaises(ValueError):
            self.tool.run(input_string)

    def test_write_existant(self):
        input_string_1 = \
"""
hello_world_42.py
```python
print("hello world!")
```
"""

        input_string_2 = \
"""
hello_world_42.py
```python
print("hello world again!")
```
"""
        self.tool.run(input_string_1)
        result = self.filesystem.get_document("/home/user/hello_world_42.py")
        self.assertEqual(result, """print("hello world!")""")
        self.tool.run(input_string_2)
        result = self.filesystem.get_document("/home/user/hello_world_42.py")
        self.assertEqual(result, """print("hello world again!")""")

        