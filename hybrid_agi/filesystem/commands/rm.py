import os
from typing import List
from hybrid_agi.filesystem.commands.base import BaseShellCommand
from hybrid_agi.filesystem.filesystem import FileSystemContext

class Remove(BaseShellCommand):
    name = "rm"
    description = "remove the input file"

    def execute(self, args: List[str], ctx: FileSystemContext) -> str:
        """Method to remove a file"""
        folder_flag_str = "-r"
        folder_flag = False
        if len(args)>0:
            path = args[0]
        else:
            return "Cannot remove: Missing operand. Try 'rm --help' for more information."
        if path.startswith("-"):
            if len(args) < 2:
                return "Cannot remove: Missing operand. Try 'rm --help' for more information."
            option = args[0]
            if option == folder_flag_str:
                folder_flag = True
            else:
                return f"Cannot remove {path}: Option '{option}' not supported"
        if not self.exists(path):
            return f"Cannot remove {path}: No such file or directory"
        if folder_flag is False:
            if self.is_folder(path):
                return f"Cannot remove {path}: Is a directory"
        else:
            if not self.is_empty(path):
                return f"Cannot remove {path}: Not empty directory"
        self.hybridstore.metagraph.query('MATCH (n {name:"'+path+'"})-[:CONTAINS]->(m) DETACH DELETE m')
        self.hybridstore.metagraph.query('MATCH (n {name:"'+path+'"}) DETACH DELETE n')
        return f"Sucessfully removed {path}"

    def get_instructions(self) -> str:
        return "The Input should be a unix-like path of the file to be removed. Use the option 'rm -r' to remove empty folders"