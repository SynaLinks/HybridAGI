## Knowledge base related tools.
## Copyright (C) 2023 SynaLinks.
##
## This program is free software: you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with this program. If not, see <https://www.gnu.org/licenses/>.

class AskKnowledgeGraph(BaseTool):
    hybridstore: RedisGraphVectorStore
    name = "AskKnowledgeGraph"
    description = f"""
    Usefull to check facts and find links between entities inside a file or folder.
    The Input should have the destination path on the first line and then the question to ask.
    """
    def _run(self, query:str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        """Use the tool."""
        path = query.split("\n")[0]
        question = "\n".join(query.split("\n")[1:])
        raise NotImplementedError("Not implemented yet")

    async def _arun(self, query: str,  run_manager: Optional[AsyncCallbackManagerForToolRun] = None) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("Not implemented yet")

