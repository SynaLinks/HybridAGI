import os
from typing import List
from hybrid_agi.filesystem.commands.base import BaseShellCommand
from hybrid_agi.filesystem.filesystem import FileSystemContext

class ChangeDirectory(BaseShellCommand):
    name = "cd"
    description = "change the current working directory"

    def execute(self, args: List[str], ctx: FileSystemContext) -> str:
        """Method to change directory"""
        if len(args)>0:
            path = args[0]
            path = ctx.eval_path(path)
            if self.exists(path):
                if self.is_file(path):
                    raise ValueError(f"Cannot change directory {path}: Not a directory")
            else:
                raise ValueError(f"Cannot change directory {path}: No such file or directory")
            ctx.previous_working_directory = ctx.working_directory
            ctx.working_directory = path
            return f"Successfully changed working directory {path}"
        return "Cannot change directory: Input path not provided."

    def get_instructions(self) -> str:
        return "The Input should be a unix-like path."