"""The read program tool. Copyright (C) 2023 SynaLinks. License: GPL-3.0"""

from typing import Optional
from pydantic.v1 import Extra
from langchain.callbacks.manager import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)
from langchain.tools import BaseTool
from ..hybridstores.program_memory.program_memory import ProgramMemory

class ReadProgramTool(BaseTool):
    program_memory: ProgramMemory

    def __init__(
            self,
            program_memory: ProgramMemory,
            name = "ReadProgram",
            description = \
    """
    Usefull when you want to read a program.
    The Input should be the program name
    """):
        super().__init__(
            name = name,
            description = description,
            program_memory = program_memory)

    class Config:
        """Configuration for this pydantic object."""
        extra = Extra.forbid
        arbitrary_types_allowed = True

    def _run(
            self,
            query:str,
            run_manager: Optional[CallbackManagerForToolRun] = None
        ) -> str:
        program = self.program_memory.get_content(query.strip('"'))
        if program:
            return program
        else:
            return "Nothing found, please ensure the name is correct"

    def _arun(
            self,
            query:str,
            run_manager: Optional[AsyncCallbackManagerForToolRun] = None
        ) -> str:
        return self._run(query)