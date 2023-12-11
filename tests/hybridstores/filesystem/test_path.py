import unittest
from hybridagi.hybridstores.filesystem.path import join, dirname, basename

class TestFileSystemFunc(unittest.TestCase):
    
    def test_join(self):
        result = join(["this", "is", "a", "test"])
        self.assertEqual(result, "this/is/a/test")

    def test_dirname_empty(self):
        result = dirname("")
        self.assertEqual(result, "/")

    def test_dirname_root(self):
        result = dirname("/")
        self.assertEqual(result, "/")

    def test_dirname_one_folder(self):
        result = dirname("test")
        self.assertEqual(result, "/")

    def test_dirname(self):
        result = dirname("this/is/a/test")
        self.assertEqual(result, "this/is/a")

    def test_basename_one_folder(self):
        result = basename("test")
        self.assertEqual(result, "test")
    
    def test_basename(self):
        result = basename("this/is/a/test")
        self.assertEqual(result, "test")
