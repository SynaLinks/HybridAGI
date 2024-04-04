"""The ls command. Copyright (C) 2023 SynaLinks. License: GPL-3.0"""

from typing import List
from .base import BaseShellCommand
from ...hybridstores.filesystem.context import FileSystemContext
from ...hybridstores.filesystem.filesystem import FileSystem
from ...hybridstores.filesystem.path import basename
from ...parsers.path import PathOutputParser

class ListDirectory(BaseShellCommand):
    path_parser: PathOutputParser = PathOutputParser()

    def __init__(self, filesystem: FileSystem):
        super().__init__(
            filesystem = filesystem,
            name = "ls",
            description = "list the given directory"
        )

    def execute(self, args: List[str], ctx: FileSystemContext) -> str:
        """Method to list folder/directory"""
        result_list = []
        if len(args)>0:
            path = args[0]
            path = self.path_parser.parse(path)
        else:
            path = ctx.working_directory
        if path.startswith("-"):
            option = args[0]
            raise ValueError(f"Cannot list: Option {option} not supported")
        path = ctx.eval_path(path)
        if self.filesystem.exists(path):
            if not self.filesystem.is_folder(path):
                raise ValueError(f"Cannot list {path}: Not a directory")
        else:
            raise ValueError(f"Cannot list {path}: No such file or directory")
        result_query = self.filesystem.hybridstore.query(
            'MATCH (f:Folder {name:"'+path+'"})-[:CONTAINS]->(n:Folder) RETURN n'
        )
        for record in result_query.result_set:
            folder_name = record[0].properties["name"]
            result_list.append(basename(folder_name))
        result_query = self.filesystem.hybridstore.query(
            'MATCH (f:Folder {name:"'+path+'"})-[:CONTAINS]->(n:Document) RETURN n'
        )
        for record in result_query.result_set:
            document_name = record[0].properties["name"]
            result_list.append(basename(document_name))
        return " ".join(result_list)

    def get_instructions(self) -> str:
        return "The Input should be a unix-like path"