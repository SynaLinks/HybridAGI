"""The pwd command. Copyright (C) 2023 SynaLinks. License: GPL-3.0"""

from typing import List
from .base import BaseShellCommand
from ...hybridstores.filesystem.context import FileSystemContext
from ...hybridstores.filesystem.filesystem import FileSystem

class PrintWorkingDirectory(BaseShellCommand):

    def __init__(self, filesystem: FileSystem):
        super().__init__(
            filesystem,
            "pwd",
            "print the current working directory")

    def execute(self, args: List[str], ctx: FileSystemContext) -> str:
        return ctx.working_directory

    def get_instructions(self) -> str:
        return "No input needed."