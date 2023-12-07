"""The load programs tool. Copyright (C) 2023 SynaLinks. License: GPL-3.0"""

from typing import Optional
from pydantic.v1 import Extra
from langchain.callbacks.manager import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)
from langchain.tools import BaseTool
from ..hybridstores.program_memory.program_memory import ProgramMemory
from hybridagikb import FileOutputParser

class LoadProgramsTool(BaseTool):
    program_memory: ProgramMemory
    file_parser = FileOutputParser()

    def __init__(
            self,
            program_memory: ProgramMemory,
            name = "LoadPrograms",
            description = \
    """
    Usefull when you want to write into a new file.
    The Input should follow the following format:
    FILENAME
    ```LANG
    CONTENT
    ```
    Where the following tokens must be replaced such that:
    FILENAME is the lowercase file name including the file extension.
    LANG is the markup code block language for the content's language
    and CONTENT its content.
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

    def _run(
            self,
            query:str,
            run_manager: Optional[CallbackManagerForToolRun] = None
        ) -> str:
        filenames, contents, _ = self.file_parser.parse(query)
        self.program_memory.program_tester.verify_programs(
            filenames,
            contents
        )
        self.program_memory.add_programs(
            filenames,
            contents)
        return f"Successfully loaded {len(filenames)} programs"

    def _arun(
            self,
            query:str,
            run_manager: Optional[AsyncCallbackManagerForToolRun] = None
        ) -> str:
        raise NotImplementedError("LoadPrograms does not support async")