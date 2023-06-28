"""The virtual shell tool. Copyright (C) 2023 SynaLinks. License: GPL-3.0"""

import shlex
from typing import Optional, Type, List, Tuple, Callable
from pydantic import BaseModel, Extra, Field, root_validator
from langchain.base_language import BaseLanguageModel
from langchain.callbacks.manager import AsyncCallbackManagerForToolRun, CallbackManagerForToolRun
from langchain.tools import BaseTool, StructuredTool, Tool, tool
from hybrid_agi.filesystem.filesystem import VirtualFileSystem
from hybrid_agi.filesystem.shell import VirtualShell

from hybrid_agi.parsers.path import PathOutputParser

class CommandInputSchema(BaseModel):
    command: str

class VirtualShellTool(BaseTool):
    virtual_shell: VirtualShell

    class Config:
        """Configuration for this pydantic object."""
        extra = Extra.forbid
        arbitrary_types_allowed = True

    def __init__(
            self,
            virtual_shell: VirtualShell = None,
            name: str = "VirtualShell",
            description: str = "Usefull to navigate into your hybrid database and organize it"
        ):
        description = \
    f"""
    {description}
    You can use the following commands to interact with your hybrid memory: {list(virtual_shell.commands_map.keys())}
    You can only use ONE COMMAND AT A TIME, piping, redirection and multiple commands are NOT supported.
    Use the parameter --help for more information about the command usage.
    """
        super().__init__(
            name = name,
            description = description,
            virtual_shell = virtual_shell,
            args_schema = CommandInputSchema
        )
        
    def execute(self, command: str) -> str:
        s = shlex.shlex(command, punctuation_chars=True)
        args = list(s)
        for symbol in ["|", "||", "&", "&&", ">", ">>", "<", "<<", ";"]:
            if symbol in args:
                raise ValueError("Piping, redirection and multiple commands are not supported: Use one command at a time, without semicolon.")
        try:
            return self.virtual_shell.execute(args)
        except Exception as err:
            return str(err)

    def _run(self, query:str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        try:
            return self.execute(query.strip())
        except Exception as err:
            return str(err)

    def _arun(self, query:str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        return self._run(query, run_manager)