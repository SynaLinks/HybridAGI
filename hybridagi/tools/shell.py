"""The virtual shell tool. Copyright (C) 2023 SynaLinks. License: GPL-3.0"""

import shlex
from typing import Optional
from pydantic.v1 import Extra
from langchain.callbacks.manager import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun
)
from langchain.tools import BaseTool
from ..hybridstores.filesystem.filesystem import FileSystem
from ..utility.shell import ShellUtility

from ..utility.commands import (
    ChangeDirectory,
    ListDirectory,
    MakeDirectory,
    Move,
    PrintWorkingDirectory,
    Remove
)

class ShellTool(BaseTool):
    shell: ShellUtility

    class Config:
        """Configuration for this pydantic object."""
        extra = Extra.forbid
        arbitrary_types_allowed = True

    def __init__(
            self,
            filesystem: FileSystem,
            name: str = "Shell",
            description: str = \
            "Usefull to organize and navigate"+
            " into your database in a unix like fashion"
        ):
        commands = [
            ChangeDirectory(filesystem = filesystem),
            ListDirectory(filesystem = filesystem),
            MakeDirectory(filesystem = filesystem),
            Move(filesystem = filesystem),
            PrintWorkingDirectory(filesystem = filesystem),
            Remove(filesystem = filesystem),
        ]
        shell = ShellUtility(filesystem, commands)

        description = \
    f"""
    {description}
    You can use the following unix commands: {list(shell.commands_map.keys())}
    You can only use ONE COMMAND AT A TIME, \
    piping, redirection and multiple commands are NOT supported.
    """
        super().__init__(
            name = name,
            description = description,
            shell = shell
        )
        
    def execute(self, command: str) -> str:
        s = shlex.shlex(command, punctuation_chars=True)
        args = list(s)
        for symbol in ["|", "||", "&", "&&", ">", ">>", "<", "<<", ";"]:
            if symbol in args:
                raise ValueError(
                    "Piping, redirection and multiple commands are not supported:"+
                    " Use one command at a time, without semicolon."
                )
        try:
            return self.shell.execute(args)
        except Exception as err:
            return str(err)

    def _run(
            self,
            query:str,
            run_manager: Optional[CallbackManagerForToolRun] = None
        ) -> str:
        try:
            return self.execute(query.strip())
        except Exception as err:
            return str(err)

    def _arun(
            self,
            query:str,
            run_manager: Optional[AsyncCallbackManagerForToolRun] = None
        ) -> str:
        return self._run(query)