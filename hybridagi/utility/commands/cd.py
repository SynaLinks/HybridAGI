"""The cd command. Copyright (C) 2023 SynaLinks. License: GPLv3"""

from typing import List
from .base import BaseShellCommand
from ...hybridstores.filesystem.context import FileSystemContext
from ...hybridstores.filesystem.filesystem import FileSystem
from ...parsers.path import PathOutputParser

class ChangeDirectory(BaseShellCommand):

    def __init__(self, filesystem: FileSystem):
        super().__init__(
            filesystem,
            "cd",
            "change the current working directory"
        )
        self.path_parser = PathOutputParser()

    def execute(self, args: List[str], ctx: FileSystemContext) -> str:
        """Method to change directory"""
        if len(args)>0:
            path = args[0]
            path = self.path_parser.parse(path)
            path = ctx.eval_path(path)
            if self.filesystem.exists(path):
                if self.filesystem.is_file(path):
                    raise ValueError(
                        f"Cannot change directory {path}: Not a directory")
            else:
                raise ValueError(
                    f"Cannot change directory {path}: No such file or directory")
            ctx.previous_working_directory = ctx.working_directory
            ctx.working_directory = path
            return f"Successfully changed working directory {path}"
        return "Cannot change directory: Input path not provided."

    def get_instructions(self) -> str:
        return "The Input should be a unix-like path."