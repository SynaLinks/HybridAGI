## Self chat tool.
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

from typing import Optional, Type
from langchain.callbacks.manager import AsyncCallbackManagerForToolRun, CallbackManagerForToolRun
from langchain.tools import BaseTool, StructuredTool, Tool, tool
from langchain.base_language import BaseLanguageModel
from langchain.prompts.prompt import PromptTemplate
from langchain.chains.llm import LLMChain
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain

from hybrid_agi.prompt import (
    HYBRID_AGI_SELF_DESCRIPTION,
    HYBRID_AGI_CORE_VALUES
)

SELF_CHAT_TEMPLATE=\
"""
{self_description}
{core_values}

The following is a conversation with yourself.
You MUST speak in {language}.

Current conversation:

{history}
AI:"""


SELF_CHAT_PROMPT = PromptTemplate(
    input_variables=["self_description", "core_values", "language", "history"],
    template = SELF_CHAT_TEMPLATE
)

class SelfChatTool(BaseTool):
    llm: BaseLanguageModel
    memory: ConversationBufferMemory
    language: str = "English"
    name: str = "SelfChat"
    description: str =\
    """
    Usefull to create textual content using your own LLM.
    The Input should include the goal/instruction and every necessary information.
    The Observation is from your own perspective, adressed to you.
    """
    verbose = True

    def __init__(
            self,
            llm: BaseLanguageModel,
            language: str,
            verbose: bool = True
        ):
        memory = ConversationBufferMemory()
        super().__init__(
            llm = llm,
            memory = memory,
            language = language,
            verbose = verbose
        )

    def _run(self, query:str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        """Use the tool."""
        try:
            chain = LLMChain(llm=self.llm, prompt=SELF_CHAT_PROMPT, verbose = self.verbose)
            self.memory.chat_memory.add_ai_message(query)
            answer = chain.predict(
                self_description=HYBRID_AGI_SELF_DESCRIPTION,
                core_values=HYBRID_AGI_CORE_VALUES,
                language=self.language,
                history=self.memory.load_memory_variables({})["history"]
            )
            self.memory.chat_memory.add_ai_message(answer)
            return answer
        except Exception as err:
            return str(err)

    async def _arun(self, query: str,  run_manager: Optional[AsyncCallbackManagerForToolRun] = None) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("SelfChat does not support async")