"""The shell utility. Copyright (C) 2023 SynaLinks. License: GPL-3.0"""

from typing import List
from ..hybridstores.filesystem.filesystem import FileSystem
from .commands.base import BaseShellCommand

class ShellUtility():
    """The shell for the filesystem"""
    def __init__(
            self,
            filesystem: FileSystem,
            commands: List[BaseShellCommand]):
        """The shell utility constructor"""
        self.filesystem = filesystem
        self.commands_map = {}
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
            raise ValueError(
                "Please use one of the following commands: "+
                str(list(self.commands_map.keys())))

