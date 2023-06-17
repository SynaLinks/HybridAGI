import os
from typing import List
from hybrid_agi.filesystem.commands.base import BaseShellCommand
from hybrid_agi.filesystem.filesystem import FileSystemContext, dirname

class Move(BaseShellCommand):
    name = "mv"
    description = "move the target file or folder into the destination file"

    def execute(self, args: List[str], ctx: FileSystemContext) -> str:
        """Method to move a file or folder"""
        target_path = ""
        destination_path = ""
        if len(args) < 2:
            raise ValueError("Cannot move: Missing file operand. Try 'rm --help' for more information.")
        target_path = args[0]
        destination_path = args[1]
               
        target_path = ctx.eval_path(target_path)
        destination_path = ctx.eval_path(destination_path)

        if not self.exists(target_path):
            raise ValueError(f"Cannot move: {target_path}: No such file")
        if self.exists(destination_path):
            raise ValueError(f"Cannot move: File of directory already exist")

        if dirname(target_path) == dirname(destination_path):
            # If same directory, just rename the file
            params = {"new_name": destination_path}
            self.hybridstore.metagraph.query('MATCH (n {name:"'+target_path+'"}) SET n.name=$destination_path', params)
        else:
            # Otherwise remove the Folder's edge and recreate it + rename
            self.hybridstore.metagraph.query('MATCH (n {name:"'+target_path+'"})<-[r:CONTAINS]-(m:Folder) DELETE r')
            self.hybridstore.metagraph.query('MATCH (n:Folder {name:"'+dirname(destination_path)+'"}), (m {name:"'+target_path+'"}) MERGE (n)-[:CONTAINS]->(m)')
            params = {"new_name": destination_path}
            self.hybridstore.metagraph.query('MATCH (n {name:"'+target_path+'"}) SET n.name=$destination_path', params)
        return f"Sucessfully moved"

    def get_instructions(self) -> str:
        return "The Input should be the unix-like target path then the unix-like destination path."

