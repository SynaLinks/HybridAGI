from typing import List
from .path import dirname, join

class FileSystemContext():

    """The filesystem context"""
    def __init__(self):
        self.initialize()

    def eval_path(self, path: str) -> str:
        """Method to eval unix-like path"""
        if path != "":
            if path.startswith(".."):
                path = dirname(self.working_directory) + path[2:]
            elif path.startswith("."):
                path = self.working_directory + path[1:]
            elif path.startswith("~"):
                path = self.home_directory + path[1:]
            elif path == "-":
                path = self.previous_working_directory
            if not path.startswith("/"):
                if self.working_directory == "/":
                    path = self.working_directory + path
                else:
                    path = join([self.working_directory, path])
        else:
            path = self.working_directory
        return path

    def eval_paths(self, paths: List[str]) -> List[str]:
        evaluated_paths = []
        for path in paths:
            evaluated_paths.append(self.eval_path(path))
        return evaluated_paths

    def initialize(self):
        self.home_directory = "/home/user"
        self.working_directory = "/home/user"
        self.previous_working_directory = "/home/user"