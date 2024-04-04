"""The mkdir command. Copyright (C) 2023 SynaLinks. License: GPL-3.0"""

from typing import List
from .base import BaseShellCommand
from ...hybridstores.filesystem.context import FileSystemContext
from ...hybridstores.filesystem.filesystem import FileSystem
from ...hybridstores.filesystem.path import dirname
from ...parsers.path import PathOutputParser

class MakeDirectory(BaseShellCommand):
    path_parser: PathOutputParser = PathOutputParser()

    def __init__(self, filesystem: FileSystem):
        super().__init__(
            filesystem = filesystem,
            name = "mkdir",
            description = "make a new directory",
        )

    def execute(self, args: List[str], ctx: FileSystemContext) -> str:
        """Method to create a directory"""
        if len(args)==0:
            raise ValueError(
                "Cannot create directory: Missing operand."+
                " Try `mkdir --help` for more information."
                )
        nb_dir = 0
        args = args[0].split()
        for path in args:
            path = self.path_parser.parse(path)
            if path.startswith("-"):
                raise ValueError("Cannot create directory: Options not supported")
            path = ctx.eval_path(path)
            if self.filesystem.exists(path):
                raise ValueError(f"Cannot create directory {path}: File exists")
            parent_folder = dirname(path)
            if not self.filesystem.exists(parent_folder):
                raise ValueError(
                    f"Cannot create directory {path}:"+
                    f" '{parent_folder}' No such file or directory"
                )
            self.filesystem.create_folder(path)
            nb_dir += 1
        if nb_dir == 1:
            return f"Sucessfully created directory {path}"
        return f"Sucessfully created {nb_dir} directories"
 
    def get_instructions(self) -> str:
        return "The Input should be a unix-like path of the folder to be created"