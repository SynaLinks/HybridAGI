"""The similarity search tool. Copyright (C) 2023 SynaLinks. License: GPL-3.0"""

from typing import Optional
from langchain.callbacks.manager import AsyncCallbackManagerForToolRun, CallbackManagerForToolRun
from langchain.tools import BaseTool, StructuredTool, Tool, tool

class SimilaritySearch(BaseTool):
    hybridstore: RedisGraphHybridStore
    name = "SimilaritySearch"
    description = f"""
    Usefull to find similar content.
    The Input should be the content to find.
    """
    def _run(self, query:str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        """Use the tool."""
        try:
            retreiver = self.hybridstore.as_retreiver()

        except Exception as err:
            return str(err)

    async def _arun(self, query: str,  run_manager: Optional[AsyncCallbackManagerForToolRun] = None) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("Not implemented yet")

