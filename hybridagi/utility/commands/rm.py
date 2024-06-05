"""The rm command. Copyright (C) 2023 SynaLinks. License: GPL-3.0"""

from typing import List
from .base import BaseShellCommand
from ...hybridstores.filesystem.context import FileSystemContext
from ...hybridstores.filesystem.filesystem import FileSystem
from ...output_parsers.path import PathOutputParser

class Remove(BaseShellCommand):

    def __init__(self, filesystem: FileSystem):
        super().__init__(
            filesystem = filesystem,
            name = "rm",
            description = "remove the input file or empty folder",
        )
        self.path_parser = PathOutputParser()

    def execute(self, args: List[str], ctx: FileSystemContext) -> str:
        """Method to remove a file or empty folder"""
        if len(args)>0:
            path = args[0]
            path = self.path_parser.parse(path)
            path = ctx.eval_path(path)
        else:
            return "Cannot remove: Missing operand."+\
                " Try 'rm --help' for more information."
        if path.startswith("-"):
            raise ValueError("Cannot remove: Options not supported")
        if not self.filesystem.exists(path):
            raise ValueError(f"Cannot remove {path}: No such file or directory")
        if not self.filesystem.is_empty(path):
            return ValueError(f"Cannot remove {path}: Not empty directory")
        params = {"path": path}
        self.filesystem.hybridstore.query(
            'MATCH (n {name:$path})-[:CONTAINS]->(m) DETACH DELETE m',
            params = params,
        )
        self.filesystem.hybridstore.query(
            'MATCH (n {name:$path}) DETACH DELETE n',
            params = params,
        )
        return f"Sucessfully removed {path}"

    def get_instructions(self) -> str:
        return "The Input should be a unix-like path of the file to be removed."+\
            " Use the option 'rm -r' to remove empty folders"