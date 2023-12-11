"""The upload tool. Copyright (C) 2023 SynaLinks. License: GPL-3.0"""

from typing import Optional
from pydantic.v1 import Extra
from langchain.callbacks.manager import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun
)
from langchain.tools import BaseTool
from ..hybridstores.filesystem.filesystem import FileSystem
from ..parsers.path import PathOutputParser
from langchain.schema import BaseOutputParser
from ..utility.archiver import ArchiverUtility

class UploadTool(BaseTool):
    filesystem: FileSystem
    downloads_directory: str
    archiver: ArchiverUtility
    path_parser: BaseOutputParser = PathOutputParser()

    class Config:
        """Configuration for this pydantic object."""
        extra = Extra.forbid
        arbitrary_types_allowed = True

    def __init__(
            self,
            filesystem: FileSystem,
            downloads_directory: str,
            name:str = "Upload",
            description:str = \
    """
    Usefull to upload a folder or file to the User.
    The Input should be the target path.
    """
        ):
        archiver = ArchiverUtility(
            filesystem = filesystem,
            downloads_directory = downloads_directory)
        super().__init__(
            name = name,
            description = description,
            filesystem = filesystem,
            downloads_directory = downloads_directory,
            archiver = archiver
        )

    def upload(self, path:str) -> str:
        try:
            path = self.path_parser.parse(path)
            path = self.filesystem.context.eval_path(path)
            self.archiver.zip_and_download(path)
            return "Successfully uploaded"
        except Exception as err:
            return str(err)

    def _run(
            self,
            query:str,
            run_manager: Optional[CallbackManagerForToolRun] = None
        ) -> str:
        return self.upload(query)

    def _arun(
            self,
            query:str,
            run_manager: Optional[AsyncCallbackManagerForToolRun] = None
        ) -> str:
        return self._run(query)