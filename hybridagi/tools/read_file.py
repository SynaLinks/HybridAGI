"""The read file tool. Copyright (C) 2023 SynaLinks. License: GPL-3.0"""

from typing import Optional
from pydantic.v1 import Extra
from langchain.callbacks.manager import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun
)
from langchain.tools import BaseTool
from ..hybridstores.filesystem.filesystem import FileSystem
from ..utility.reader import ReaderUtility
from ..parsers.path import PathOutputParser

class ReadFileTool(BaseTool):
    filesystem: FileSystem
    reader: ReaderUtility
    path_parser = PathOutputParser()

    class Config:
        """Configuration for this pydantic object."""
        extra = Extra.forbid
        arbitrary_types_allowed = True

    def __init__(
            self,
            filesystem: FileSystem,
            name = "ReadFile",
            description = \
    """
    Usefull when you want to read or check an existing file.
    The input should be a string containing the target path.
    Display one chunk at a time, use multiple times with the same target to scroll.
    """
        ):
        reader = ReaderUtility(filesystem)
        super().__init__(
            name = name,
            description = description,
            filesystem = filesystem,
            reader = reader,
        )

    def read_file(self, path: str) -> str:
        try:
            path = self.path_parser.parse(path)
            path = self.filesystem.context.eval_path(path)
            return self.reader.read_document(path)
        except Exception as err:
            return str(err)

    def _run(
            self,
            query:str,
            run_manager: Optional[CallbackManagerForToolRun] = None
        ) -> str:
        return self.read_file(query.strip())

    def _arun(
            self,
            query:str,
            run_manager: Optional[AsyncCallbackManagerForToolRun] = None
        ) -> str:
        return self._run(query)