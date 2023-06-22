"""The mkdir command. Copyright (C) 2023 SynaLinks. License: GPLv3"""

import os
from typing import List
from hybrid_agi.filesystem.commands.base import BaseShellCommand
from hybrid_agi.filesystem.filesystem import FileSystemContext, dirname

class MakeDirectory(BaseShellCommand):
    name:str = "mkdir"
    description:str = "make a new directory"

    def execute(self, args: List[str], ctx: FileSystemContext) -> str:
        """Method to create a directory"""
        if len(args)==0:
            raise ValueError("Cannot create directory: Missing operand. Try 'mkdir --help' for more information.")
        path = args[0]         
        if path.startswith("-"):
            raise ValueError(f"Cannot create directory: Options not supported")
        path = ctx.eval_path(path)
        if self.exists(path):
            raise ValueError(f"Cannot create directory {path}: File exists")
        parent_folder = dirname(path)
        if not self.exists(parent_folder):
            raise ValueError(f"Cannot create directory {parent_folder}: No such file or directory")
        self.create_folder(path)
        return f"Sucessfully created directory {path}"
 
    def get_instructions(self) -> str:
        return "The Input should be a unix-like path of the folder to be created"