"""The ls command. Copyright (C) 2023 SynaLinks. License: GPLv3"""

import os
from typing import List
from hybrid_agi.filesystem.commands.base import BaseShellCommand
from hybrid_agi.filesystem.filesystem import FileSystemContext, basename
from hybrid_agi.parsers.path import PathOutputParser

class ListDirectory(BaseShellCommand):
    name: str = "ls"
    description: str = "list the input directory"
    path_parser = PathOutputParser()

    def execute(self, args: List[str], ctx: FileSystemContext) -> str:
        """Method to list folder/directory"""
        result_list = ""
        if len(args)>0:
            path = args[0]
            path = self.path_parser.parse(path)
        else:
            path = ctx.working_directory
        if path.startswith("-"):
            option = args[0]
            raise ValueError(f"Cannot list: Option {option} not supported.")
        path = ctx.eval_path(path)
        if self.exists(path):
            if not self.is_folder(path):
                raise ValueError(f"Cannot list {path}: Not a directory")
        else:
            raise ValueError(f"Cannot list {path}: No such file or directory.")
        result_query = self.hybridstore.metagraph.query('MATCH (f:Folder {name:"'+path+'"})-[:CONTAINS]->(n:Folder) RETURN n')
        for record in result_query.result_set:
            folder_name = record[0].properties["name"]
            result_list += basename(folder_name)+" "
        result_query = self.hybridstore.metagraph.query('MATCH (f:Folder {name:"'+path+'"})-[:CONTAINS]->(n:Document) RETURN n')
        for record in result_query.result_set:
            document_name = record[0].properties["name"]
            result_list += basename(document_name)+" "
        return result_list

    def get_instructions(self) -> str:
        return "The Input should be a unix-like path."