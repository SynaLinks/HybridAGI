import os
import abc
from typing import Optional, List
from pydantic import BaseModel, Extra
from hybrid_agi.filesystem.filesystem import FileSystemContext, FileSystemUtility

class BaseShellCommand(FileSystemUtility):
    name: Optional[str] = None
    description: Optional[str] = None

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
            self.validate_args(args)
            if args[0] == "--help":
                return self.get_instructions()
            else:
                return self.execute(args, ctx)

    def validate_args(self, args):
        for forbid in [";", "&","&&","|", "||", ">", ">>", "<", "<<"]:
            if forbid in args:
                cmd = ' '.join(args)
                raise ValueError(f"Failed to execute '{cmd}': Piping, redirection and multiple commands are not supported.")