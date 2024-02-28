import os
import unittest
from langchain_community.embeddings import FakeEmbeddings
from hybridagi import FileSystem
from hybridagi.tools import UploadTool

class TestUploadTool(unittest.TestCase):
    def setUp(self):
        self.redis_url = "redis://localhost:6379"
        self.index_name = "test"
        self.verbose = False
        self.embeddings = FakeEmbeddings(size=512)
        self.embeddings_dim = 512
        self.downloads_directory = "tests/tools/archives"
        self.filesystem = FileSystem(
            redis_url = self.redis_url,
            index_name = self.index_name,
            embeddings = self.embeddings,
            embeddings_dim = self.embeddings_dim,
            verbose = self.verbose
        )
        self.filesystem.clear()
        self.filesystem.initialize()
        self.tool = UploadTool(filesystem = self.filesystem,
        downloads_directory = self.downloads_directory)

    def test_upload_file(self):
        self.filesystem.add_documents(
            ["/home/user/test.txt"],
            ["test document"])
        result = self.tool.run("test.txt")
        self.assertEqual(result, "Successfully uploaded")

    def test_upload_folder(self):
        self.filesystem.create_folder("/home/user/Test")
        self.filesystem.create_folder("/home/user/Test/Test2")
        self.filesystem.add_documents(
            ["/home/user/Test/test.txt", "/home/user/Test/Test2/test2.txt"],
            ["test document 1", "test document 2"])
        result = self.tool.run("Test")
        self.assertEqual(result, "Successfully uploaded")

    def tearDown(self):
        for f in os.listdir(self.downloads_directory):
            if f.endswith(".zip"):
                os.remove(os.path.join(self.downloads_directory, f))
