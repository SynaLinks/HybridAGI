"""The action reasoner. Copyright (C) 2023 SynaLinks. License: GPL-3.0"""

import asyncio
from typing import Dict, Optional, Callable
from langchain.prompts import PromptTemplate
from langchain.tools import BaseTool
from .decision_reasoner import DecisionReasoner

TOOL_INPUT_TEMPLATE = \
"""{context}
Action Purpose: {purpose}
Action: {tool_name}
Action Input Prompt: {tool_prompt}

Please ensure to use the following format to Answer:

Thought: Your reasoning to infer the action input in a step by step way to be sure to have the right answer.
Action Input: The input of the action that follow the above action prompt.

Please, ensure to always use the above format to answer"""

TOOL_INPUT_PROMPT = PromptTemplate(
    input_variables = ["context", "purpose", "tool_name", "tool_prompt"],
    template = TOOL_INPUT_TEMPLATE
)

class ActionReasoner(DecisionReasoner):
    """LLM reasoner that can use tools to act"""
    tools_map: Dict[str, BaseTool] = {}

    pre_action_callback: Optional[
        Callable[
            [str, str, str],
            None
        ]
    ] = None
    post_action_callback: Optional[
        Callable[
            [str, str, str, str],
            None
        ]
    ] = None

    def get_action_prompt_without_context(
            self,
            purpose: str,
            tool_name:str,
            tool_prompt: str,
        ) -> str:
        """Returns the action prompt without context"""
        return TOOL_INPUT_TEMPLATE.format(
            context = "",
            purpose = purpose,
            tool_name = tool_name,
            tool_prompt = tool_prompt,
        )

    def get_action_context(
            self,
            purpose: str,
            tool_name: str,
            tool_prompt: str,
        ) -> str:
        """Returns the action context"""
        tool_prompt = self.get_action_prompt_without_context(
            purpose = purpose,
            tool_name = tool_name,
            tool_prompt = tool_prompt,
        )
        context = self.trace_memory.get_context(
            tool_prompt,
            self.smart_llm_max_token,
        )
        return context

    async def async_predict_tool_input(
            self,
            purpose: str,
            tool_name:str,
            tool_prompt: str,
        ) -> str:
        """Method to asynchronously predict the tool's input parameters"""
        context = self.get_action_context(
            purpose = purpose,
            tool_name = tool_name,
            tool_prompt = tool_prompt,
        )
        prediction = await self.async_predict(
            prompt = TOOL_INPUT_PROMPT,
            context = context,
            purpose = purpose,
            tool_name = tool_name,
            tool_prompt = tool_prompt,
            use_smart_llm = True,
        )
        if self.debug:
            print(prediction)
        return prediction

    def predict_tool_input(
            self,
            purpose: str,
            tool_name:str,
            tool_prompt: str
        ) -> str:
        """Method to predict the tool's input parameters"""
        context = self.get_action_context(
            purpose = purpose,
            tool_name = tool_name,
            tool_prompt = tool_prompt,
        )
        prediction = self.predict(
            prompt = TOOL_INPUT_PROMPT,
            context = context,
            purpose = purpose,
            tool_name = tool_name,
            tool_prompt = tool_prompt,
            use_smart_llm = True,
        )
        if self.debug:
            print(prediction)
        return prediction

    def perform_action(
            self,
            purpose: str,
            tool_name:str,
            tool_prompt: str,
            disable_inference: bool = False,
        ) -> str:
        """Method to perform an action"""
        if self.pre_action_callback is not None:
            self.pre_action_callback(
                purpose,
                tool_name,
                tool_prompt,
            )
        if disable_inference:
            tool_input = tool_prompt
        else:
            tool_input = self.predict_tool_input(
                purpose = purpose,
                tool_name = tool_name,
                tool_prompt = tool_prompt,
            )
        self.validate_tool(tool_name)
        tool_observation = self.execute_tool(tool_name, tool_input)
        self.trace_memory.commit_action(
            purpose = purpose,
            tool_name = tool_name,
            tool_input = tool_input,
            tool_observation = tool_observation,
        )
        if self.post_action_callback is not None:
            self.post_action_callback(
                purpose,
                tool_name,
                tool_input,
                tool_observation,
            )
        return tool_observation

    async def async_perform_action(
            self,
            purpose: str,
            tool_name: str,
            tool_prompt: str,
            disable_inference: bool = False,
        ) -> str:
        """Method to asynchronously perform an action"""
        if self.pre_action_callback is not None:
            asyncio.create_task(
                self.pre_action_callback(
                    purpose,
                    tool_name,
                    tool_prompt,
                )
            )
        if disable_inference:
            tool_input = tool_prompt
        else:
            tool_input = await self.async_predict_tool_input(
                purpose = purpose,
                tool_name = tool_name,
                tool_prompt = tool_prompt,
            )
        self.validate_tool(tool_name)
        tool_observation = self.execute_tool(tool_name, tool_input)
        self.trace_memory.commit_action(
            purpose = purpose,
            tool_name = tool_name,
            tool_input = tool_input,
            tool_observation = tool_observation,
        )
        if self.post_action_callback is not None:
            asyncio.create_task(
                self.post_action_callback(
                    purpose,
                    tool_name,
                    tool_input,
                    tool_observation,
                )
            )
        return tool_observation

    def validate_tool(self, tool_name: str):
        """Method to validate the given tool_name"""
        if tool_name not in self.tools_map:
            raise ValueError(
                f"Tool '{tool_name}' not registered. Please use another one.")

    def execute_tool(self, tool_name:str, tool_input:str):
        """Method to execute the given tool"""
        try:
            return self.tools_map[tool_name].run(tool_input)
        except Exception as err:
            return str(err)

    async def async_execute_tool(self, tool_name:str, tool_input:str):
        """Method to asynchronously execute the given tool"""
        try:
            return await self.tools_map[tool_name].arun(tool_input)
        except Exception as err:
            return str(err)
            
