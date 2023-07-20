"""The ask user tool for chainlit. Copyright (C) 2023 SynaLinks. License: GPL-3.0"""

import chainlit as cl
from typing import Optional
from langchain.callbacks.manager import AsyncCallbackManagerForToolRun, CallbackManagerForToolRun

from hybrid_agi.tools.ask_user import AskUserTool

class UIAskUserTool(AskUserTool):
    def _run(self, query:str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        res = cl.AskUserMessage(content=query, timeout=300).send()
        if res:
            return "The User responded with: "+res["content"]
        else:
            return "The User did not respond"