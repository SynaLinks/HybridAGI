import chainlit as cl
from typing import Optional
from langchain.callbacks.manager import AsyncCallbackManagerForToolRun, CallbackManagerForToolRun

from hybrid_agi.tools.display_text import DisplayTextTool

class UIDisplayTextTool(DisplayTextTool):
    def _run(self, query:str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        cl.Text(name="Check this out please!", text=query, display="inline").send()
        return "Sucessfully display"
