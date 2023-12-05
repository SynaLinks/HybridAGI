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
Decision: {question}

Please ensure to use the following format to Answer:

Step 1: First reasoning step to answer to the Decision
Step 2: Second reasoning step to answer to the Decision
... and so on (max 5 reasoning steps)
Final Step (must be {choice}):...

Please, always use the above format to answer"""

DECISION_PROMPT = PromptTemplate(
    input_variables = ["context", "purpose", "question", "choice"],
    template = DECISION_TEMPLATE
)

EVALUATION_TEMPLATE = \
"""
{context}
Action Purpose: {purpose}
Action: {tool}
Action Input Prompt: {prompt}
Action Input: {tool_input}

Evaluation: Please, evaluate the quality of the above Action Input
It is better when less assumption are made.

Please ensure to use the following format to Answer:

Step 1: First reasoning step to evaluate the above Action Input
Step 2: Second reasoning step to evaluate the above Action Input
... and so on (max 5 reasoning steps)
Final Step (must be a score between 0.0 and 1.0):...

Please, always use the above format to answer"""

EVALUATION_PROMPT = PromptTemplate(
    input_variables = ["context", "purpose", "tool", "prompt", "tool_input"],
    template = EVALUATION_TEMPLATE
)

TOOL_INPUT_TEMPLATE = \
"""{context}
Action Purpose: {purpose}
Action: {tool}
Action Input Prompt: {prompt}
Action Input:"""

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
    max_evaluation_attemp: int = 5

    verbose: bool = True
    debug: bool = True

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
            disable_inference: bool = False,
            ranked_inferences: int = 1
        ) -> str:
        """Method to perform an action"""
        if self.pre_action_callback is not None:
            self.pre_action_callback(purpose, tool, prompt)
        if ranked_inferences == 0:
            disable_inference = True
        if disable_inference:
            tool_input = prompt
        else:
            tool_input = ""
            if ranked_inferences == 1:
                tool_input = self.predict_tool_input(purpose, tool, prompt)
            else:
                predictions = []
                scores = []
                for i in range(0, ranked_inferences):
                    pred = self.predict_tool_input(purpose, tool, prompt)
                    predictions.append(pred)
                    score = self.perform_evaluation(
                        purpose,
                        tool,
                        prompt,
                        pred)
                    scores.append(score)
                prediction_score_pairs = zip(predictions, scores)
                sorted_predictions = sorted(prediction_score_pairs, key=lambda x: x[1], reverse=True)
                best_prediction, _ = sorted_predictions[0]
                tool_input = best_prediction
                
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
            if disable_inference:
                observation = ""
            else:
                observation = tool_input
            tool_input = prompt
            action = action_template.format(
                purpose = purpose,
                tool = tool,
                prompt = tool_input + "\n" + observation)
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
                context = "",
                purpose = purpose,
                question = question,
                choice = choice)
            encoding = tiktoken.get_encoding("cl100k_base")
            num_tokens = len(encoding.encode(decision_prompt))
            context = self.working_memory.get_trace(self.fast_llm_max_token-num_tokens)
            result = chain.predict(
                context = context,
                purpose = purpose,
                question = question,
                choice = choice)
            if self.debug:
                print("Decision:" +result)
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

    def perform_evaluation(
            self,
            purpose: str,
            tool: str,
            prompt: str,
            tool_input: str) -> float:
        """Method to perform an evaluation of the tool's input inference"""
        chain = LLMChain(llm=self.fast_llm, prompt=EVALUATION_PROMPT, verbose=self.debug)
        attemps = 0
        while attemps < self.max_evaluation_attemp:
            evaluation_prompt = EVALUATION_TEMPLATE.format(
                context = "",
                purpose = purpose,
                tool = tool,
                prompt = prompt,
                tool_input = tool_input)
            encoding = tiktoken.get_encoding("cl100k_base")
            num_tokens = len(encoding.encode(evaluation_prompt))
            context = self.working_memory.get_trace(self.fast_llm_max_token-num_tokens)
            result = chain.predict(
                context = context,
                purpose = purpose,
                tool = tool,
                prompt = prompt,
                tool_input = tool_input)
            result = self.output_parser.parse(result)
            score = result.split()[-1].upper()
            score = score.strip(".")
            if self.debug:
                print("Evaluation:" +result)
            try:
                return float(score)
            except Exception:
                pass
            attemps += 1
        raise ValueError(
            f"Failed to evaluate after {attemps} attemps."+
            f" Got {result} should be a score between 0.0 and 1.0.")

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
