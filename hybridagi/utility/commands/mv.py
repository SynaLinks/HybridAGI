"""The mv command. Copyright (C) 2023 SynaLinks. License: GPL-3.0"""

from typing import List
from .base import BaseShellCommand
from ...hybridstores.filesystem.context import FileSystemContext
from ...hybridstores.filesystem.filesystem import FileSystem
from ...hybridstores.filesystem.path import dirname
from ...parsers.path import PathOutputParser

class Move(BaseShellCommand):
    path_parser: PathOutputParser = PathOutputParser()

    def __init__(self, filesystem: FileSystem):
        super().__init__(
            filesystem = filesystem,
            name = "mv",
            description = "move the target file or folder to destination",
        )

    def execute(self, args: List[str], ctx: FileSystemContext) -> str:
        """Method to move a file or folder"""
        target_path = ""
        destination_path = ""
        if len(args) < 2:
            raise ValueError(
                "Cannot move: Missing file operand."+
                " Try 'rm --help' for more information."
            )
        target_path = args[0]
        target_path = self.path_parser.parse(target_path)
        destination_path = args[1]
        destination_path = self.path_parser.parse(destination_path)
               
        target_path = ctx.eval_path(target_path)
        destination_path = ctx.eval_path(destination_path)

        if not self.filesystem.exists(target_path):
            raise ValueError(f"Cannot move: {target_path}: No such file")
        if self.filesystem.exists(destination_path):
            raise ValueError("Cannot move: File or directory already exists")

        if dirname(target_path) == dirname(destination_path):
            # If same directory, just rename the file
            self.filesystem.query(
                'MATCH (n {name:"'+target_path+'"}) SET n.name="'+destination_path+'"')
        else:
            # Otherwise remove the Folder's edge and recreate it + rename
            self.filesystem.query(
                'MATCH (n {name:"'+
                target_path+'"})<-[r:CONTAINS]-(m:Folder) DELETE r')
            folder_path = dirname(destination_path)
            self.filesystem.query(
                'MATCH (n:Folder {name:"'+folder_path+'"}),'+
                ' (m {name:"'+target_path+'"}) MERGE (n)-[:CONTAINS]->(m)')
            self.filesystem.query(
                'MATCH (n {name:"'+target_path+'"}) SET n.name="'+destination_path+'"')
        return "Sucessfully moved"

    def get_instructions(self) -> str:
        return "The Input should be the unix-like target path"+\
            " then the unix-like destination path."

