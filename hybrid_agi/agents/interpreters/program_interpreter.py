from typing import List, Optional
from pydantic import BaseModel, Extra
from colorama import Fore, Style
from redisgraph import Node, Graph 
from collections import OrderedDict

from langchain.chains.llm import LLMChain
from langchain.tools import Tool
from langchain.base_language import BaseLanguageModel
from hybrid_agi.hybridstores.redisgraph import RedisGraphHybridStore
from langchain.prompts.prompt import PromptTemplate

class GraphProgramInterpreter(BaseModel):
    """LLM based interpreter for graph programs"""
    hybridstore: RedisGraphHybridStore
    llm: BaseLanguageModel
    program_key: str
    program: Optional[Graph] = None
    prompt: str = ""
    default_prompt: str = ""
    max_iteration: int = 50
    allowed_tools: List[str] = []
    tools_map: OrderedDict[str, Tool] = {}
    language: str = "English"
    monitoring: bool = False,
    verbose: bool = True

    class Config:
        """Configuration for this pydantic object."""
        extra = Extra.forbid
        arbitrary_types_allowed = True

    def __init__(
            self,
            hybridstore: RedisGraphHybridStore,
            llm: BaseLanguageModel,
            program_key:str = "",
            prompt:str = "",
            tools:List[Tool] = [],
            max_iteration: int = 50,
            language: str = "English",
            monitoring: bool = False,
            verbose: bool = True
        ):
        if program_key == "":
            program_key = hybridstore.main.name
        program = Graph(program_key, hybridstore.client)
        super().__init__(
            hybridstore = hybridstore,
            llm = llm,
            program_key = program_key,
            program = program,
            prompt = prompt,
            default_prompt = prompt,
            language = language,
            monitoring = monitoring,
            verbose = verbose
        )
        for tool in tools:
            self.allowed_tools.append(tool.name)
            self.tools_map[tool.name] = tool

    def run(self, objective:str):
        self.clear()
        self.update(f"The objective given by the User is: {objective}\n")
        result = self.program.query('MATCH (n:Control {name:"Start"}) RETURN n')
        if len(result.result_set) == 0:
            raise ValueError("No entry point in the program")
        if len(result.result_set) > 1:
            raise ValueError("Multiple entry point in the program")
        starting_node = result.result_set[0][0]
        current_node = self.get_next(starting_node)
        next_node = None
        iteration = 0
        while True:
            if current_node.label == "Action":
                self.use_tool(current_node)
                next_node = self.get_next(current_node)
                if self.monitoring is True:
                    self.monitor()
            elif current_node.label == "Decision":
                next_node = self.decide(current_node)
            elif current_node.label == "Control":
                if current_node.properties["name"] == "End":
                    break
                if next_node is None:
                    return "Program failed after reaching a non-terminated path"
            if iteration > self.max_iteration:
                return "Program failed after reaching max iteration"
            current_node = next_node
        return "Program Success"

    def get_next(self, node:Node) -> Optional[Node]:
        name = node.properties["name"]
        result = self.program.query('MATCH ({name:"'+name+'"})-[:NEXT]->(n) RETURN n')
        if len(result.result_set) > 0:
            return result.result_set[0][0]
        return None

    def predict(self, prompt:str) -> str:
        """Predict the next words"""
        prompt_template = PromptTemplate.from_template(self.prompt+"\n"+prompt)
        chain = LLMChain(llm=self.llm, prompt=prompt_template, verbose=False)
        prediction = chain.predict(language=self.language)
        return prediction

    def decide(self, node:Node) -> Node:
        # get possible output options
        question = node.properties["name"]
        purpose = node.properties["purpose"]
        prompt = f"Decision: {question} Please answer without additional information.\nDecision Purpose: {purpose}\n"
        outcomes = []
        result = self.program.query('MATCH (n:Decision {name:"'+question+'", purpose:"'+purpose+'"})-[r]->() RETURN type(r)')
        for record in result.result_set:
            outcomes.append(record[0])
        choice = " or ".join(outcomes)
        prompt += f"Decision Answer (must be {choice}):"
        decision = ""
        while True:
            decision = self.predict(prompt)
            if decision in outcomes:
                break
        prompt += decision
        result = self.program.query('MATCH (:Decision {name:"'+question+'", purpose:"'+purpose+'"})-[:'+decision+']->(n) RETURN n')
        next_node = result.result_set[0][0]
        self.update(prompt)
        return next_node

    def use_tool(self, node:Node) -> str:
        """Method to use a tool"""
        action_purpose = node.properties["name"]
        tool_name = node.properties["tool"]
        tool_params_prompt = node.properties["params"]
        tool_prompt = f"Action: {tool_name}\nAction Purpose: {action_purpose}\nAction Input: {tool_params_prompt}"
        tool_input = self.predict(tool_prompt)
        observation = self.execute_tool(tool_name, tool_input)
        final_prompt = f"Action: {tool_name}\nAction Purpose: {action_purpose}\nAction Input: {tool_input}\nAction Observation:{observation}"
        self.update(final_prompt)

    def execute_tool(self, name:str, query:str):
        """Method to run the given tool"""
        if name not in self.allowed_tools:
            raise ValueError(f"Tool '{name}' not allowed. Please use another one.")
        if name not in self.tools_map:
            (f"Tool '{name}' not registered. Please use another one.")
        try:
            return self.tools_map[name].run(query)
        except Exception as err:
            return str(err)

    def update(self, prompt:str):
        """Method to update the program prompt"""
        if self.verbose:
            if prompt.startswith("Action:"):
                print(f"{Fore.YELLOW}{prompt}{Style.RESET_ALL}")
            elif prompt.startswith("Decision:"):
                print(f"{Fore.BLUE}{prompt}{Style.RESET_ALL}")
            else:
                print(f"{prompt}")
        self.prompt += "\n" + prompt

    def monitor(self):
        """Method to monitor the process"""
        prompt = "You are an expert in self-reflexion. Please reflect on your actions and decisions but never answer them.\nCritique:"
        critique = self.predict(prompt)
        self.update(prompt + " " + critique)

    def clear(self):
        """Clear the prompt"""
        self.prompt = self.default_prompt