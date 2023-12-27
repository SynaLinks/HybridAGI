"""The browse website tool. Copyright (C) 2023 SynaLinks. License: GPL-3.0"""

from typing import Optional
from pydantic.v1 import Extra
from langchain.callbacks.manager import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun
)
from langchain.tools import BaseTool
from ..hybridstores.filesystem.filesystem import FileSystem
from ..utility.browser import BrowserUtility

class BrowseWebsiteTool(BaseTool):
    filesystem: FileSystem
    browser: BrowserUtility

    class Config:
        """Configuration for this pydantic object."""
        extra = Extra.forbid
        arbitrary_types_allowed = True

    def __init__(
            self,
            filesystem: FileSystem,
            user_agent: str,
            name = "BrowseWebsite",
            description = \
    """
    Usefull when you want to browse an existing website.
    The input should be the target url.
    Display one chunk at a time, use multiple times with the same target to scroll.
    """
        ):
        browser = BrowserUtility(
            filesystem=filesystem,
            user_agent=user_agent,
        )
        super().__init__(
            name = name,
            description = description,
            filesystem = filesystem,
            browser = browser,
        )

    def browse_website(self, url: str) -> str:
        try:
            return self.browser.browse_website(url)
        except Exception as err:
            return str(err)

    def _run(
            self,
            query:str,
            run_manager: Optional[CallbackManagerForToolRun] = None
        ) -> str:
        return self.browse_website(query.strip())

    def _arun(
            self,
            query:str,
            run_manager: Optional[AsyncCallbackManagerForToolRun] = None
        ) -> str:
        return self._run(query)