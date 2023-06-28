"""The virtual shell. Copyright (C) 2023 SynaLinks. License: GPL-3.0"""

import os
import datetime
from pydantic import BaseModel, Extra
from typing import Optional, List, Dict, Callable
from langchain.schema import Document
from langchain.base_language import BaseLanguageModel
from hybrid_agi.hybridstores.redisgraph import RedisGraphHybridStore
from hybrid_agi.filesystem.commands.base import BaseShellCommand
from hybrid_agi.filesystem.filesystem import FileSystemContext, VirtualFileSystem

class VirtualShell(BaseModel):
    """The virtual shell for the filesystem."""
    hybridstore: RedisGraphHybridStore
    filesystem: VirtualFileSystem
    commands_map: Dict[str, BaseShellCommand] = {}

    class Config:
        """Configuration for this pydantic object."""
        extra = Extra.forbid
        arbitrary_types_allowed = True
    
    def __init__(self,
            hybridstore: RedisGraphHybridStore,
            filesystem: VirtualFileSystem,
            commands: List[BaseShellCommand]
        ):
        super().__init__(
            hybridstore = hybridstore,
            filesystem = filesystem,
        )
        for cmd in commands:
            self.commands_map[cmd.name] = cmd

    def execute(self, args:List[str]) -> str:
        """Execute a shell-like command"""
        if len(args) > 0:
            cmd = args[0]
            arguments = args[1:]
            if cmd in self.commands_map.keys():
                return self.commands_map[cmd].run(arguments, self.filesystem.context)
            else:
                raise ValueError(f"Command '{cmd}' not supported")
        else:
            raise ValueError(f"Please use one of the following command: {list(self.commands_map.keys())}")

