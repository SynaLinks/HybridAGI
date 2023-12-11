"""The content search tool. Copyright (C) 2023 SynaLinks. License: GPL-3.0"""

from typing import Optional
from pydantic.v1 import Extra
from langchain.callbacks.manager import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)
from langchain.tools import BaseTool
from ..hybridstores.filesystem.filesystem import FileSystem

class ContentSearchTool(BaseTool):
    filesystem: FileSystem

    def __init__(
            self,
            filesystem: FileSystem,
            name = "ContentSearch",
            description = \
    """
    Usefull when you want to search for a similar content.
    The input should be the description of the content to look for.
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

    def content_search(self, query: str) -> str:
        """Use the tool."""
        result = self.filesystem.similarity_search(query, fetch_content=True)
        if len(result) > 0:
            return result[0]
        else:
            return "Nothing found"

    def _run(
            self,
            query:str,
            run_manager: Optional[CallbackManagerForToolRun] = None
        ) -> str:
        return self.content_search(query)

    def _arun(
            self,
            query:str,
            run_manager: Optional[AsyncCallbackManagerForToolRun] = None
        ) -> str:
        return self._run(query)