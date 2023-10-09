"""The speak tool. Copyright (C) 2023 SynaLinks. License: GPL-3.0"""

from colorama import Fore, Style
from typing import Optional
from langchain.callbacks.manager import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun
)
from langchain.tools import BaseTool

class SpeakTool(BaseTool):
    name = "Speak"
    description = \
    """
    Usefull to tell information to the User.
    """
    def _run(
            self,
            query:str,
            run_manager: Optional[CallbackManagerForToolRun] = None
        ) -> str:
        """Use the tool."""
        print(f"\n{Fore.YELLOW}[*] {query}{Style.RESET_ALL}")
        return "Success"

    async def _arun(
            self,
            query: str,
            run_manager: Optional[AsyncCallbackManagerForToolRun] = None
        ) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("Speak does not support async")