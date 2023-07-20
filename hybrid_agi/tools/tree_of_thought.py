"""The tree of thought tool. Copyright (C) 2023 SynaLinks. License: GPL-3.0"""

from colorama import Fore
from colorama import Style
from typing import Optional
from langchain.callbacks.manager import AsyncCallbackManagerForToolRun, CallbackManagerForToolRun
from langchain.tools import BaseTool, StructuredTool, Tool, tool

class TreeOfThoughtTool(BaseTool):
    name = "TreeOfThought"
    description = \
    """
    Usefull to provide better answer for logical thinking or coding.
    """
    def _run(self, query:str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        """Use the tool."""
        raise NotImplementedError("Not implemented yet")

    async def _arun(self, query: str,  run_manager: Optional[AsyncCallbackManagerForToolRun] = None) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("TreeOfThought does not support async")