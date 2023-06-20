from typing import List
from hybrid_agi.filesystem.commands.base import BaseShellCommand
from hybrid_agi.filesystem.filesystem import FileSystemContext

class PrintWorkingDirectory(BaseShellCommand):
    name:str = "pwd"
    description:str = "print the current working directory"

    def execute(self, args: List[str], ctx: FileSystemContext) -> str:
        return ctx.working_directory

    def get_instructions(self) -> str:
        return "No input needed."