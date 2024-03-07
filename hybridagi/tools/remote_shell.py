"""The remote shell tool. Copyright (C) 2023 SynaLinks. License: GPL-3.0"""
from typing import Optional
from langchain.callbacks.manager import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)
from langchain.tools import BaseTool
import requests

class RemoteShellTool(BaseTool):
    sandbox_url: str
    endpoint: str

    def __init__(
            self,
            sandbox_url: str,
            endpoint: str = "/cmdexec",
            name: str = "RemoteShell",
            description: str = \
            "Usefull to run shell commands in a sandboxed environment"
        ):
        super().__init__(
            name = name,
            description = description,
            sandbox_url = sandbox_url,
            endpoint = endpoint,
        )

    def execute(self, command: str) -> str:
        payload = {"cmd": command}
        response = requests.post(self.sandbox_url+self.endpoint, json=payload)
        response.raise_for_status()
        return response.text.replace("\\n", "\n").strip("\"").strip()

    def _run(
            self,
            query:str,
            run_manager: Optional[CallbackManagerForToolRun] = None
        ) -> str:
        try:
            query = query.strip("`")
            query = query.strip()
            return self.execute(query)
        except Exception as err:
            return str(err)

    def _arun(
            self,
            query:str,
            run_manager: Optional[AsyncCallbackManagerForToolRun] = None
        ) -> str:
        return self._run(query)