import unittest
from hybridagi import FileSystemContext

class TestFileSystemCtxt(unittest.TestCase):
    def setUp(self):
        self.ctxt = FileSystemContext()
        self.ctxt.initialize()

    def test_constructor(self):
        self.assertEqual(self.ctxt.home_directory, "/home/user")
        self.assertEqual(self.ctxt.working_directory, "/home/user")
        self.assertEqual(self.ctxt.previous_working_directory, "/home/user")
    
    def test_initialize(self):
        self.ctxt.working_directory = "/this"
        self.ctxt.home_directory = "/this/is/a/test"
        self.ctxt.previous_working_directory = "/this/is"
        self.ctxt.initialize()
        self.assertEqual(self.ctxt.home_directory, "/home/user")
        self.assertEqual(self.ctxt.working_directory, "/home/user")
        self.assertEqual(self.ctxt.previous_working_directory, "/home/user")

    def test_eval_no_effect(self):
        path = "/this/is/a/test"
        result = self.ctxt.eval_path(path)
        self.assertEqual(result, "/this/is/a/test")

    def test_eval_current(self):
        path = "."
        result = self.ctxt.eval_path(path)
        self.assertEqual(result, "/home/user")

    def test_eval_current_relative(self):
        path = "./this/is/a/test"
        result = self.ctxt.eval_path(path)
        self.assertEqual(result, "/home/user/this/is/a/test")
    
    def test_eval_parent(self):
        path = ".."
        result = self.ctxt.eval_path(path)
        self.assertEqual(result, "/home")

    def test_eval_parent_relative(self):
        path = "../this/is/a/test"
        result = self.ctxt.eval_path(path)
        self.assertEqual(result, "/home/this/is/a/test")

    def test_eval_home(self):
        path = "~"
        result = self.ctxt.eval_path(path)
        self.assertEqual(result, "/home/user")

    def test_eval_home_relative(self):
        path = "~/this/is/a/test"
        result = self.ctxt.eval_path(path)
        self.assertEqual(result, "/home/user/this/is/a/test")

    def test_eval_previous(self):
        self.ctxt.previous_working_directory = "/"
        path = "-"
        result = self.ctxt.eval_path(path)
        self.assertEqual(result, "/")

    def test_eval_working_root(self):
        self.ctxt.working_directory = "/"
        path = "this/is/a/test"
        result = self.ctxt.eval_path(path)
        self.assertEqual(result, "/this/is/a/test")

    def test_eval_working(self):
        self.ctxt.working_directory = "/home/user"
        path = "this/is/a/test"
        result = self.ctxt.eval_path(path)
        self.assertEqual(result, "/home/user/this/is/a/test")
