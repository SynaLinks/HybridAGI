"""The cd command. Copyright (C) 2023 SynaLinks. License: GPLv3"""

import os
from typing import List
from hybrid_agi.filesystem.commands.base import BaseShellCommand
from hybrid_agi.filesystem.filesystem import FileSystemContext
from hybrid_agi.parsers.path import PathOutputParser

class ChangeDirectory(BaseShellCommand):
    name :str = "cd"
    description :str = "change the current working directory"
    path_parser = PathOutputParser()

    def execute(self, args: List[str], ctx: FileSystemContext) -> str:
        """Method to change directory"""
        if len(args)>0:
            path = args[0]
            path = self.path_parser.parse(path)
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