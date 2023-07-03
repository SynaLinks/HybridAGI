"""The simulator tools. Copyright (C) 2023 SynaLinks. License: GPL-3.0"""

from typing import Optional
from langchain.callbacks.manager import AsyncCallbackManagerForToolRun, CallbackManagerForToolRun
from langchain.tools import BaseTool, StructuredTool, Tool, tool

class LoadProgramTool(BaseTool):
    hybridstore: RedisGraphVectorStore
    name = "LoadProgram"
    description = f"""
    Usefull to load a Cypher program for testing
    """
    def _run(self, query:str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        """Use the tool."""
        raise NotImplementedError("Not implemented yet")

    async def _arun(self, query: str,  run_manager: Optional[AsyncCallbackManagerForToolRun] = None) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("Not implemented yet")

class SimulateProgramTool(BaseTool):
    hybridstore: RedisGraphVectorStore
    tools = List[BaseTool] = []
    tools = List[BaseTool] = []
    name = "SimulateProgram"
    description = f"""
    Usefull to simulate the execution of a Cypher graph program for testing
    """

    def _run(self, query:str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        """Use the tool."""
        program_interpreter = None
        simulated_user_memory = ConversationBufferMemory()
        raise NotImplementedError("Not implemented yet")

    async def _arun(self, query: str,  run_manager: Optional[AsyncCallbackManagerForToolRun] = None) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("Not implemented yet")