from typing import OrderedDict, List
from pydantic import BaseModel
from langchain.chains.llm import LLMChain
from langchain.prompts.prompt import PromptTemplate
from langchain.base_language import BaseLanguageModel
from langchain.tools import Tool

DECISION_TEMPLATE = \
"""{context}
Decision Purpose: {purpose}
Decision: {question} Let's think this out in a step by step way to sure to have the right answer.
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
    """ """
    llm: BaseLanguageModel

    allowed_tools: List[str] = []
    tools_map: OrderedDict[str, Tool] = {}

    max_decision_attemps: int = 5

    verbose: bool = True
    debug: bool = False

    def predict_tool_input(self, context: str, purpose: str, tool:str, prompt: str) -> str:
        chain = LLMChain(llm=self.llm, prompt=TOOL_INPUT_PROMPT, verbose=self.debug)
        prediction = chain.predict(
            context = context,
            purpose = purpose,
            tool = tool,
            prompt = prompt
        )
        if self.debug:
            print(prediction)
        return prediction

    def perform_action(self, context: str, purpose: str, tool:str, prompt: str):
        tool_input = self.predict_tool_input(context, purpose, tool, prompt)
        action_template = \
        "Action Purpose: {purpose}\nAction: {tool}\nAction Input: {prompt}"""

        if tool != "Predict":
            self.validate_tool(tool)
            observation = self.execute_tool(tool, tool_input)

            action = action_template.format(
                    purpose = purpose,
                    tool = tool,
                    prompt = tool_input + f"\nAction Observation: {observation}"
            )
        else:
            action = action_template.format(
                    purpose = purpose,
                    tool = tool,
                    prompt = prompt + tool_input
            )
        return action

    def perform_decision(
            self,
            context: str, 
            purpose:str, 
            question: str,
            options: List[str]
        ) -> str:
        """Method to decide using a LLM"""
        chain = LLMChain(llm=self.llm, prompt=DECISION_PROMPT, verbose=self.debug)
        choice = " or ".join(options)
        attemps = 0
        while attemps < self.max_decision_attemps:
            result = chain.predict(
                context=context,
                purpose=purpose,
                question=question,
                choice=" or ".join(options))
            if self.debug:
                print(result)
            decision = result.split()[-1].upper()
            decision = decision.strip(".")
            if decision in options:
                break
            attemps += 1
        if decision not in options:
            raise ValueError(
                f"Failed to decide after {attemps} attemps."+
                f" Got {result} should be {choice},"+
                " please verify your prompts or programs."
            )
        return decision

    def validate_tool(self, name):
        if name not in self.allowed_tools:
            raise ValueError(f"Tool '{name}' not allowed. Please use another one.")
        if name not in self.tools_map:
            raise ValueError(f"Tool '{name}' not registered. Please use another one.")

    def execute_tool(self, name:str, query:str):
        """Method to run the given tool"""
        try:
            return self.tools_map[name].run(query)
        except Exception as err:
            return str(err)
