from .base import BaseToolKit
from ..tools.remote_shell import RemoteShellTool

class CodeToolKit(BaseToolKit):
    sandbox_url: str

    def __init__(self, sandbox_url: str):

        tools = [
            RemoteShellTool(sandbox_url = sandbox_url)
        ]
        super().__init__(
            sandbox_url = sandbox_url,
            tools = tools,
        )