"""The base class for shell commands. Copyright (C) 2023 SynaLinks. License: GPL-3.0"""

import abc
from pydantic.v1 import BaseModel
from typing import List
from ...hybridstores.filesystem.context import FileSystemContext
from ...hybridstores.filesystem.filesystem import FileSystem

class BaseShellCommand(BaseModel):
    filesystem: FileSystem
    name: str = ""
    description: str = ""

    @abc.abstractmethod
    def execute(self, args: List[str], ctx: FileSystemContext) -> str:
        pass

    @abc.abstractmethod
    def get_instructions(self) -> str:
        pass

    def run(self, args: List[str], ctx: FileSystemContext)-> str:
        """Run the command"""
        if len(args) > 0:
            if args[0] == "--help":
                return self.get_instructions()
        return self.execute(args, ctx)