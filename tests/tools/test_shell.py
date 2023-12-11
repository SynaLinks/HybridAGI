import unittest
from langchain.embeddings import FakeEmbeddings
from hybridagi import FileSystem
from hybridagi.tools import ShellTool

class TestShellTool(unittest.TestCase):
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
        self.tool = ShellTool(filesystem = self.filesystem)

    def test_cd(self):
        result = self.tool.run("cd /home")
        self.assertEqual(result, "Successfully changed working directory /home")

    def test_ls(self):
        result = self.tool.run("ls")
        self.assertEqual(result, "Downloads Documents Pictures Music")

    def test_mkdir(self):
        result = self.tool.run("mkdir Tests")
        self.assertEqual(result, "Sucessfully created directory /home/user/Tests")

    def test_mv(self):
        self.tool.run("mkdir Tests")
        result = self.tool.run("mv Tests RenamedTests")
        self.assertEqual(result, "Sucessfully moved")

    def test_pwd(self):
        result = self.tool.run("pwd")
        self.assertEqual(result, "/home/user")

    def test_rm(self):
        self.tool.run("mkdir Tests")
        result = self.tool.run("rm Tests")
        self.assertEqual(result, "Sucessfully removed /home/user/Tests")

    def test_invalid(self):
        result = self.tool.run("echo 'hello !'")
        self.assertEqual(result, "Command 'echo' not supported")

    def test_multiple(self):
        result = self.tool.run("echo 'hello !' >> test.txt")
        self.assertEqual(result,
        "Piping, redirection and multiple commands are not supported: "+\
        "Use one command at a time, without semicolon.")


    

    
