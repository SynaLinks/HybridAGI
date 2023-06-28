"""The speak tool. Copyright (C) 2023 SynaLinks. License: GPL-3.0"""

from colorama import Fore
from colorama import Style
from typing import Optional
from langchain.callbacks.manager import AsyncCallbackManagerForToolRun, CallbackManagerForToolRun
from langchain.tools import BaseTool, StructuredTool, Tool, tool

class SpeakTool(BaseTool):
    language:str = "English"
    name = "Speak"
    description = f"""
    Usefull to tell information.
    The input MUST be a question in {language}.
    """
    def _run(self, query:str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        """Use the tool."""
        print(f"\n{Fore.GREEN}[*] "+query+f"{Style.RESET_ALL}")
        return "Success"

    async def _arun(self, query: str,  run_manager: Optional[AsyncCallbackManagerForToolRun] = None) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("Speak does not support async")