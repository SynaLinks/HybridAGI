import os
import abc
from typing import Optional, List
from pydantic import BaseModel, Extra
from hybrid_agi.filesystem.filesystem import FileSystemContext, FileSystemUtility

class BaseShellCommand(FileSystemUtility):
    name: str
    description: str

    class Config:
        """Configuration for this pydantic object."""
        extra = Extra.forbid
        arbitrary_types_allowed = True

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