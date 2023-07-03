"""The mock speak tool. Copyright (C) 2023 SynaLinks. License: GPL-3.0"""

from colorama import Fore
from colorama import Style
from typing import Optional
from langchain.callbacks.manager import AsyncCallbackManagerForToolRun, CallbackManagerForToolRun
from langchain.tools import BaseTool, StructuredTool, Tool, tool
from langchain.memory import ConversationBufferMemory

class MockSpeakTool(BaseTool):
    user_memory: ConversationBufferMemory
    language:str = "English"
    name = "Speak"
    description = f"""
    Usefull to tell information to the User.
    The input MUST be a question in {language}.
    """
    def _run(self, query:str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        """Use the tool."""
        user_memory.chat_memory.add_ai_message(query)
        return "Success"

    async def _arun(self, query: str,  run_manager: Optional[AsyncCallbackManagerForToolRun] = None) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("Speak does not support async")