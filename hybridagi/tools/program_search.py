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
    Usefull when you want to search for relevant programs.
    The input should be the description of the program to look for.
    """
        ):
        super().__init__(
            name = name,
            description = description,
            program_memory = program_memory)

    class Config:
        """Configuration for this pydantic object."""
        extra = Extra.forbid
        arbitrary_types_allowed = True

    def program_search(self, query: str) -> str:
        """Use the tool."""
        result = self.program_memory.similarity_search(query, k = 15)
        result_string = "Top-5 most relevant implemented programs:"
        n = 0
        for program_name in result:
            if not self.program_memory.program_tester.is_protected(program_name):
                description = \
                    self.program_memory.get_content_description(program_name)
                if description:
                    result_string += f"\n- {program_name}: {description}"
                else:
                    result_string += f"\n- {program_name}"
                n += 1
            if n >= 5:
                break
        return result_string

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
        return self._run(query)