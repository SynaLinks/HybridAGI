"""The mock ask user tool. Copyright (C) 2023 SynaLinks. License: GPL-3.0"""

from colorama import Fore
from colorama import Style
from typing import Optional
from langchain.callbacks.manager import AsyncCallbackManagerForToolRun, CallbackManagerForToolRun
from langchain.tools import BaseTool, StructuredTool, Tool, tool
from langchain.memory import ConversationBufferMemory

ASK_USER_MOCK_TEMPLATE =\
"""
You are a human interacting with an AI system. Please answer as best as you can.

{history}
Human:"""

ASK_USER_MOCK_PROMPT = PromptTemplate(
    template = ASK_USER_MOCK_TEMPLATE,
    input_variables = ["history"]
)

class MockAskUserTool(AskUserTool):
    user_memory: ConversationBufferMemory
    llm: Optional[BaseLanguageModel] = None

    def _run(self, query:str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        """Use the tool."""
        user_memory.chat_memory.add_ai_message(query)
        history = memory.load_memory_variables({})
        if self.llm is not None:
            chain = LLMChain(llm=self.llm, prompt=ASK_USER_MOCK_PROMPT)
            response = chain.predict(history=history)
        else:
            response = ""
        user_memory.chat_memory.add_user_message(response)
        if response:
            return "The User responded with: "+response
        else:
            return "The User did not respond"
