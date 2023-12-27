"""The web toolkit. Copyright (C) 2023 SynaLinks. License: GPL-3.0"""

from .base import BaseToolKit
from hybridagi import FileSystem
from hybridagi.tools import (
    BrowseWebsiteTool,
)

from langchain.tools import (
    Tool,
    DuckDuckGoSearchResults,
)
from langchain.utilities import ArxivAPIWrapper

class WebToolKit(BaseToolKit):
    filesystem: FileSystem
    user_agent: str

    def __init__(
            self,
            filesystem: FileSystem,
            user_agent: str,
        ):
        search_result = DuckDuckGoSearchResults()
        browse_website = BrowseWebsiteTool(filesystem, user_agent=user_agent)
        arxiv_search = ArxivAPIWrapper()

        tools = [
            Tool(
                name = "InternetSearch",
                description = search_result.description,
                func = search_result.run,
            ),
            Tool(
                name = "Arxiv",
                description = "A wrapper around Arxiv.org. Useful for when you need "+
                "to search for answers from scientific articles on arxiv.org. "+
                "Input should be a search query.",
                func = arxiv_search.run
            ),
            browse_website,
        ]

        super().__init__(
            filesystem = filesystem,
            user_agent = user_agent,
            tools = tools,
        )