"""The ask user tool. Copyright (C) 2023 SynaLinks. License: GPLv3"""

from colorama import Fore
from colorama import Style
from typing import Optional
from langchain.callbacks.manager import AsyncCallbackManagerForToolRun, CallbackManagerForToolRun
from langchain.tools import BaseTool, StructuredTool, Tool, tool

class AskUserTool(BaseTool):
    language:str = "English"
    name = "AskUser"
    description = f"""
    Usefull to ask additional information.
    The Input MUST be a question in {language}.
    The Observation is from the perspective of the User responding to you.
    """
    def _run(self, query:str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        """Use the tool."""
        print(f"\n{Fore.YELLOW}[*] "+query+f"{Style.RESET_ALL}")
        response = input(f"{Fore.YELLOW}> {Style.RESET_ALL}")
        return "User response: "+response

    async def _arun(self, query: str,  run_manager: Optional[AsyncCallbackManagerForToolRun] = None) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("AskUser does not support async")

