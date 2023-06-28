"""The speak tool for chainlit. Copyright (C) 2023 SynaLinks. License: GPL-3.0"""

import chainlit as cl
from typing import Optional
from langchain.callbacks.manager import AsyncCallbackManagerForToolRun, CallbackManagerForToolRun

from hybrid_agi.tools.speak import SpeakTool

class UISpeakTool(SpeakTool):
    def _run(self, query:str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        res = cl.Message(content=query).send()
        if res:
            return "Success"
        else:
            return "Failed"