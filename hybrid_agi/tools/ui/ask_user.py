import chainlit as cl
from typing import Optional
from langchain.callbacks.manager import AsyncCallbackManagerForToolRun, CallbackManagerForToolRun

from hybrid_agi.tools.ask_user import AskUserTool

class UIAskUserTool(AskUserTool):
    def _run(self, query:str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        res = cl.AskUserMessage(content=query, timeout=30).send()
        if res:
            return "User response: "+res["content"]
        else:
            return "User response:"