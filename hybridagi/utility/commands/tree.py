"""The tree command. Copyright (C) 2023 SynaLinks. License: GPL-3.0"""

from typing import List, Tuple
from .base import BaseShellCommand
from ...hybridstores.filesystem.context import FileSystemContext
from ...hybridstores.filesystem.filesystem import FileSystem
from ...hybridstores.filesystem.path import basename
from ...parsers.path import PathOutputParser

ELBOW = "└──"
TEE = "├──"
PIPE_PREFIX = "│   "
SPACE_PREFIX = "    "

class Tree(BaseShellCommand):

    def __init__(self, filesystem: FileSystem):
        super().__init__(
            filesystem,
            "tree",
            "display the given directory structure",
        )
        self.path_parser = PathOutputParser()

    def execute(self, args: List[str], ctx: FileSystemContext) -> str:
        """Method to display the directory structure"""
        result_list = []
        if len(args)>0:
            path = args[0]
            path = self.path_parser.parse(path)
        else:
            path = ctx.working_directory
        if path.startswith("-"):
            option = args[0]
            raise ValueError(f"Cannot use tree: Option {option} not supported")
        path = ctx.eval_path(path)
        if self.filesystem.exists(path):
            if not self.filesystem.is_folder(path):
                raise ValueError(f"Cannot use tree {path}: Not a directory")
        else:
            raise ValueError(f"Cannot use tree {path}: No such file or directory")
        
        result_list.append(path)
        result_list, folder_count, file_count = self._get_tree(path, result_list, "", 0, 0)
        result_list.append(f"{folder_count} directories, {file_count} files")
        return "\n".join(result_list)

    def get_instructions(self) -> str:
        return "The Input should be a unix-like path"

    def _get_tree(
            self: str,
            path: str,
            result: List[str],
            prefix: str,
            folder_count: int,
            file_count: int,
        ) -> Tuple[List[str], int, int]:
        """Recursively gather the tree structure"""
        files = self._get_files(path)
        directories = self._get_subdirectories(path)

        for i, item in enumerate(directories):
            is_last = i == len(directories) - 1
            prefix_str = ELBOW if is_last else TEE
            result.append(f"{prefix}{prefix_str} {basename(item)}")
            folder_count += 1
            new_prefix = prefix + SPACE_PREFIX if is_last else prefix + PIPE_PREFIX
            result, folder_count, file_count = self._get_tree(item, result, new_prefix, folder_count, file_count)

        for i, item in enumerate(files):
            is_last = i == len(files) - 1
            prefix_str = ELBOW if is_last else TEE
            result.append(f"{prefix}{prefix_str} {basename(item)}")
            file_count += 1
        
        return result, folder_count, file_count

    def _get_subdirectories(self, path: str) -> List[str]:
        """Retrieve the folders of the given folder."""
        query = 'MATCH (f:Folder {name:"'+path+'"})-[:CONTAINS]->(n:Folder) RETURN n'
        result_query = self.filesystem.query(query)
        return sorted(record[0].properties["name"] for record in result_query)

    def _get_files(self, path: str) -> List[str]:
        """Retrieve the files of the given folder."""
        query = 'MATCH (f:Folder {name:"'+path+'"})-[:CONTAINS]->(n:Document) RETURN n'
        result_query = self.filesystem.query(query)
        return sorted(record[0].properties["name"] for record in result_query)