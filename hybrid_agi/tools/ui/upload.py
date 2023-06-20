import os
import chainlit as cl
from typing import Optional
from langchain.callbacks.manager import AsyncCallbackManagerForToolRun, CallbackManagerForToolRun

from hybrid_agi.parsers.path import PathOutputParser
from hybrid_agi.tools.upload import UploadTool


class UIUploadTool(UploadTool):

    def _run(self, query:str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        try:
            path = self.path_parser.parse(query)
            path = self.filesystem.context.eval_path(path)
            filename = self.zip_and_download(path)
            absolute_path = os.path.abspath(filename)
            cl.Message(
                content=f"Successfully archived into: [archive](file://{absolute_path})"
            ).send()
        except Exception as err:
            return err
    
