"""The simulator tools. Copyright (C) 2023 SynaLinks. License: GPL-3.0"""

from redisgraph import Graph
from typing import Optional
from langchain.callbacks.manager import AsyncCallbackManagerForToolRun, CallbackManagerForToolRun
from langchain.tools import BaseTool, StructuredTool, Tool, tool

from hybrid_agi.hybridstores.redisgraph import RedisGraphHybridStore
from hybrid_agi.tools.mock.speak import MockSpeakTool
from hybrid_agi.tools.mock.ask_user import MockAskUserTool

class LoadGraphProgramTool(BaseTool):
    hybridstore: RedisGraphHybridStore
    name = "LoadGraphProgram"
    description = \
    """
    Usefull to load into testing playground a Cypher program.
    The input should be a Cypher CREATE query representing a cognitive program of prompts.
    """
    def _run(self, query:str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        """Use the tool."""
        try:
            graph = Graph(self.hybridstore.playground.name, self.hybridstore.client)
            graph.delete()
            graph.query(query)
            return "Succesfully loaded"
        except Exception as err:
            return str(err)

    async def _arun(self, query: str,  run_manager: Optional[AsyncCallbackManagerForToolRun] = None) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("LoadGraphProgram does not support async")

class SimulateGraphProgramTool(BaseTool):
    hybridstore: RedisGraphVectorStore
    llm: BaseLanguageModel
    simulated_tools: List[BaseTool] = []
    simulated_user_memory: ConversationBufferMemory = ConversationBufferMemory()
    name: str = "SimulateGraphProgram"
    description: str = ""
    
    def __init__(self,
                 hybridstore,
                 tools,
                 name = "SimulateProgram",
                 description = \
    """
    Usefull to simulate the execution of a cognitive program loaded into testing playground.
    The input should be the objective to test.
    """
        ):
        super().__init__(
            hybridstore = hybridstore,
            llm = llm,
            simulated_tools = [],
            name = name,
            description = description
        )
        mock_speak = MockSpeakTool(user_memory=self.simulated_user_memory)
        mock_ask_user = MockAskUserTool(llm=self.llm, user_memory=self.simulated_user_memory)
        simulated_tools = []
        for tool in tools:
            if tool.name == mock_speak.name
                self.simulated_tools.append(mock_speak)
            elif tool.name == mock_ask_user.name
                self.simulated_tools.append(mock_ask_user)
            else:
                self.simulated_tools.append(tool)

    def _run(self, query:str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        """Use the tool."""
        interpreter = GraphProgramInterpreter(
            hybridstore,
            llm,
            program_key = self.hybridstore.playground.name
            prompt = instructions,
            final_prompt = "Summarize the complete process and critisize it, please show your work. Without additionnal information.\nCritique:",
            tools = self.simulated_tools,
            max_iteration = 30,
            monitoring = True,
            verbose = False
        )
        self.simulated_user_memory = ConversationBufferMemory()
        result = interpreter.run(query.strip())
        return result

    async def _arun(self, query: str,  run_manager: Optional[AsyncCallbackManagerForToolRun] = None) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("SimulateProgram does not support async.")