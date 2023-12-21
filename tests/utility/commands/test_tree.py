import unittest
from hybridagi import (
    Tree,
    FileSystemContext,
    FileSystem
)

from langchain.embeddings import FakeEmbeddings

class TestTree(unittest.TestCase):
    def setUp(self):
        self.embeddings = FakeEmbeddings(size=512)
        self.embeddings_dim = 512
        self.context = FileSystemContext()
        self.filesystem = FileSystem(
            redis_url = 'redis://localhost:6379',
            index_name = 'test_index',
            embeddings = self.embeddings,
            embeddings_dim = self.embeddings_dim,
            context = self.context)     
        self.filesystem.clear()
        self.filesystem.initialize()
        self.command = Tree(filesystem=self.filesystem)

    def test_tree_home(self):
        result = self.command.execute(["/home/user/"], self.context)
        expected_output = \
"""/home/user
├── Documents
├── Downloads
├── Music
└── Pictures
4 directories, 0 files"""
        self.assertEqual(result, expected_output)

    def test_tree_root_path(self):
        result = self.command.execute(["/"], self.context)
        expected_output = \
"""/
└── home
    └── user
        ├── Documents
        ├── Downloads
        ├── Music
        └── Pictures
6 directories, 0 files"""
        self.assertEqual(result, expected_output)

    def test_tree_with_doc(self):
        self.filesystem.create_document("/home/user/Documents/test_doc.txt")
        result = self.command.execute(["/"], self.context)
        expected_output = \
"""/
└── home
    └── user
        ├── Documents
        │   └── test_doc.txt
        ├── Downloads
        ├── Music
        └── Pictures
6 directories, 1 files"""
        self.assertEqual(result, expected_output)

if __name__ == '__main__':
    unittest.main()
