"""The append file tool. Copyright (C) 2023 SynaLinks. License: GPL-3.0"""

from typing import Optional
from pydantic.v1 import Extra
from langchain.callbacks.manager import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)
from langchain.tools import BaseTool
from ..hybridstores.filesystem.filesystem import FileSystem
from ..parsers.path import PathOutputParser
from ..parsers.file import FileOutputParser

class AppendFilesTool(BaseTool):
    filesystem: FileSystem
    path_parser = PathOutputParser()
    file_parser = FileOutputParser()

    def __init__(
            self,
            filesystem: FileSystem,
            name = "AppendFiles",
            description = \
    """
    Usefull when you want to append data to an existing file.
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
            filesystem = filesystem
        )

    class Config:
        """Configuration for this pydantic object."""
        extra = Extra.forbid
        arbitrary_types_allowed = True

    def _run(
            self,
            query:str,
            run_manager: Optional[CallbackManagerForToolRun] = None
        ) -> str:
        filenames, contents, languages = self.file_parser.parse(query)
        filenames = self.filesystem.context.eval_paths(filenames)
        self.filesystem.append_documents(
            filenames,
            contents,
            languages)
        return f"Successfully modified {len(filenames)} files"

    def _arun(
            self,
            query:str,
            run_manager: Optional[AsyncCallbackManagerForToolRun] = None
        ) -> str:
        return self._run(query)