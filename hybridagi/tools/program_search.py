"""The program search tool. Copyright (C) 2023 SynaLinks. License: GPL-3.0"""

from typing import Optional
from pydantic.v1 import Extra
from langchain.callbacks.manager import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)
from langchain.tools import BaseTool
from ..hybridstores.program_memory.program_memory import ProgramMemory

class ProgramSearchTool(BaseTool):
    program_memory: ProgramMemory

    def __init__(
            self,
            program_memory: ProgramMemory,
            name = "ProgramSearch",
            description = \
    """
    Usefull when you want to search for a similar program.
    The input should be the description of the program to look for.
    """
        ):
        super().__init__(
            name = name,
            description = description,
            program_memory = program_memory
        )

    class Config:
        """Configuration for this pydantic object."""
        extra = Extra.forbid
        arbitrary_types_allowed = True

    def program_search(self, query: str) -> str:
        """Use the tool."""
        result = self.program_memory.similarity_search(
            query,
            k = 1, 
            fetch_content = True)
        if len(result) > 0:
            return result[0]
        else:
            return "Nothing found"

    def _run(
            self,
            query:str,
            run_manager: Optional[CallbackManagerForToolRun] = None
        ) -> str:
        return self.program_search(query)

    def _arun(
            self,
            query:str,
            run_manager: Optional[AsyncCallbackManagerForToolRun] = None
        ) -> str:
        raise NotImplementedError("ProgramSearch does not support async")