## Virtual shell tool.
## Copyright (C) 2023 SynaLinks.
##
## This program is free software: you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with this program. If not, see <https://www.gnu.org/licenses/>.
import shlex
from typing import Optional, Type, List, Tuple
from pydantic import BaseModel, Extra, Field, root_validator
from langchain.base_language import BaseLanguageModel
from langchain.callbacks.manager import AsyncCallbackManagerForToolRun, CallbackManagerForToolRun
from langchain.tools import BaseTool, StructuredTool, Tool, tool
from hybrid_agi.filesystem.filesystem import VirtualFileSystem
from hybrid_agi.filesystem.shell import VirtualShell

from hybrid_agi.parsers.path import PathOutputParser

from inspect import signature
from langchain.tools.base import create_schema_from_function



def execute(command: str) -> str:
    args = shlex.split(command)
    if ["|", "||", "&", "&&", ">", ">>", "<", "<<", ";"] in args:
        raise ValueError("Piping, redirection and multiple commands are not supported: Use one command at a time, without semicolon.")
    return self.virtual_shell.execute(args)


class VirtualShellSchema(BaseModel):
    command : str = Field(...)

class VirtualShellTool(StructuredTool):
    virtual_shell: VirtualShell

    class Config:
        """Configuration for this pydantic object."""
        extra = Extra.forbid
        arbitrary_types_allowed = True

    def __init__(
            self,
            virtual_shell: VirtualShell,
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
        func = self.execute
        description = f"{name}{signature(func)} - {description.strip()}"
        super().__init__(
            name = name,
            description = description,
            virtual_shell = virtual_shell,
            func = func,
            args_schema = VirtualShellSchema
        )
        
    def execute(self, command: str) -> str:
        args = shlex.split(command)
        if ["|", "||", "&", "&&", ">", ">>", "<", "<<", ";"] in args:
            raise ValueError("Piping, redirection and multiple commands are not supported: Use one command at a time, without semicolon.")
        return self.virtual_shell.execute(args)

    def _run(self, query:str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        try:
            super()._run(query, run_manager)
        except Exception as err:
            return str(err)