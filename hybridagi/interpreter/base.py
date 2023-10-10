"""The base program interpreter. Copyright (C) 2023 SynaLinks. License: GPL-3.0"""

from typing import OrderedDict, List, Optional, Callable
from pydantic.v1 import BaseModel
from langchain.chains.llm import LLMChain
from langchain.prompts.prompt import PromptTemplate
from langchain.base_language import BaseLanguageModel
from langchain.tools import Tool
from .program_trace_memory import ProgramTraceMemory
import tiktoken

from ..parsers.interpreter_output_parser import InterpreterOutputParser

DECISION_TEMPLATE = \
"""{context}
Decision Purpose: {purpose}
Decision: {question} \
Let's think this out in a step by step way to be sure we have the right answer.
Decision Answer (must finish with {choice}):"""

DECISION_PROMPT = PromptTemplate(
    input_variables = ["context", "purpose", "question", "choice"],
    template = DECISION_TEMPLATE
)

TOOL_INPUT_TEMPLATE = \
"""{context}
Action Purpose: {purpose}
Action: {tool}
Action Input: {prompt}"""

TOOL_INPUT_PROMPT = PromptTemplate(
    input_variables = ["context", "purpose", "tool", "prompt"],
    template = TOOL_INPUT_TEMPLATE
)

class BaseGraphProgramInterpreter(BaseModel):
    """Base class for program interpreter"""
    smart_llm: BaseLanguageModel
    fast_llm: BaseLanguageModel

    tools_map: OrderedDict[str, Tool] = {}

    max_decision_attemp: int = 5

    verbose: bool = True
    debug: bool = False

    working_memory: ProgramTraceMemory = ProgramTraceMemory()

    output_parser = InterpreterOutputParser()

    pre_decision_callback: Optional[
        Callable[
            [str, str, List[str]],
            None
        ]
    ] = None
    post_decision_callback: Optional[
        Callable[
            [str, str, List[str], str],
            None
        ]
    ] = None

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

    class Config:
        """Configuration for this pydantic object."""
        arbitrary_types_allowed = True

    def predict_tool_input(
            self,
            purpose: str,
            tool:str,
            prompt: str
        ) -> str:
        """Method to predict the tool's input parameters"""
        tool_input_prompt = TOOL_INPUT_TEMPLATE.format(
            context = "",
            purpose = purpose,
            tool = tool,
            prompt = prompt)
        encoding = tiktoken.get_encoding("cl100k_base")
        num_tokens = len(encoding.encode(tool_input_prompt))
        context = self.working_memory.get_trace(
            self.smart_llm_max_token-num_tokens)
        chain = LLMChain(
            llm=self.smart_llm,
            prompt=TOOL_INPUT_PROMPT,
            verbose=self.debug)
        prediction = chain.predict(
            context = context,
            purpose = purpose,
            tool = tool,
            prompt = prompt)
        prediction = self.output_parser.parse(prediction)
        if self.debug:
            print(prediction)
        return prediction

    def perform_action(
            self,
            purpose: str,
            tool:str,
            prompt: str,
            disable_inference: bool = False
        ) -> str:
        """Method to perform an action"""
        if self.pre_action_callback is not None:
            self.pre_action_callback(purpose, tool, prompt)
        if disable_inference:
            tool_input = prompt
        else:
            tool_input = self.predict_tool_input(purpose, tool, prompt)
        action_template = \
        "Action Purpose: {purpose}\nAction: {tool}\nAction Input: {prompt}"""

        if tool != "Predict":
            self.validate_tool(tool)
            observation = self.execute_tool(tool, tool_input)

            action = action_template.format(
                purpose = purpose,
                tool = tool,
                prompt = tool_input + f"\nAction Observation: {observation}")
        else:
            observation = tool_input
            tool_input = prompt
            action = action_template.format(
                purpose = purpose,
                tool = tool,
                prompt = tool_input + observation)
        action = action.strip()
        if self.post_action_callback is not None:
            self.post_action_callback(purpose, tool, tool_input, observation)
        return action

    def perform_decision(
            self,
            purpose:str, 
            question: str,
            options: List[str]
        ) -> str:
        """Method to perform a decision"""
        if self.pre_decision_callback is not None:
            self.pre_decision_callback(purpose, question, options)
        chain = LLMChain(llm=self.fast_llm, prompt=DECISION_PROMPT, verbose=self.debug)
        choice = " or ".join(options)
        attemps = 0
        while attemps < self.max_decision_attemp:
            decision_prompt = DECISION_TEMPLATE.format(
                context="",
                purpose=purpose,
                question=question,
                choice=choice)
            encoding = tiktoken.get_encoding("cl100k_base")
            num_tokens = len(encoding.encode(decision_prompt))
            context = self.working_memory.get_trace(self.fast_llm_max_token-num_tokens)
            result = chain.predict(
                context = context,
                purpose = purpose,
                question = question,
                choice = choice)
            if self.debug:
                print(result)
            result = self.output_parser.parse(result)
            decision = result.split()[-1].upper()
            decision = decision.strip(".")
            if decision in options:
                break
            attemps += 1
        if decision not in options:
            raise ValueError(
                f"Failed to decide after {attemps} attemps."+
                f" Got {result} should be {choice},"+
                " please verify your prompts or programs.")
        if self.post_decision_callback is not None:
            self.post_decision_callback(purpose, question, options, decision)
        return decision

    def validate_tool(self, name):
        """Method to validate the given tool"""
        if name not in self.tools_map:
            raise ValueError(f"Tool '{name}' not registered. Please use another one.")

    def execute_tool(self, name:str, query:str):
        """Method to run the given tool"""
        try:
            return self.tools_map[name].run(query)
        except Exception as err:
            return str(err)
