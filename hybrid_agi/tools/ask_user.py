"""The ask user tool. Copyright (C) 2023 SynaLinks. License: GPL-3.0"""

from colorama import Fore
from colorama import Style
from typing import Optional
from langchain.callbacks.manager import AsyncCallbackManagerForToolRun, CallbackManagerForToolRun
from langchain.tools import BaseTool, StructuredTool, Tool, tool

class AskUserTool(BaseTool):
    name = "AskUser"
    description = \
    """
    Usefull to ask User for additionnal information.
    The Observation is from the perspective of the User responding to you.
    """
    def _run(self, query:str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        """Use the tool."""
        print(f"{Fore.YELLOW}[*] "+query+f"{Style.RESET_ALL}")
        response = input(f"> ")
        if response:
            return "The User responded with: "+response
        else:
            return "The User did not respond"

    async def _arun(self, query: str,  run_manager: Optional[AsyncCallbackManagerForToolRun] = None) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("AskUser does not support async")

