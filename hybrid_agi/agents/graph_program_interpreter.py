"""The graph program interpreter. Copyright (C) 2023 SynaLinks. License: GPL-3.0"""

from collections import deque
from typing import List, Optional, Iterable
from pydantic import BaseModel, Extra
from colorama import Fore, Style
from redisgraph import Node, Graph 
from collections import OrderedDict

from langchain.chains.llm import LLMChain
from langchain.tools import Tool
from langchain.base_language import BaseLanguageModel
from symbolinks import RedisGraphHybridStore

from hybrid_agi.reasoners.zero_shot_reasoner import ZeroShotReasoner

class GraphProgramInterpreter(ZeroShotReasoner):
    """LLM based interpreter for graph programs"""
    hybridstore: RedisGraphHybridStore
    llm: BaseLanguageModel
    program_key: str = ""
    objective: str = ""
    program_trace: str = ""
    prompt: str = ""
    monitoring_prompt: str = ""
    program_stack: Iterable = deque()
    allowed_tools: List[str] = []
    tools_map: OrderedDict[str, Tool] = {}
    language: str = "English"
    max_iterations: int = 100
    max_prompt_tokens: int = 4000
    tools_instructions: str = ""
    monitoring: bool = False
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
            monitoring_prompt:str = "",
            tools:List[Tool] = [],
            max_prompt_tokens:int = 4000,
            max_iterations:int = 100,
            language: str = "English",
            monitoring: bool = False,
            verbose: bool = True
        ):
        if program_key == "":
            program_key = hybridstore.main.name
        if not monitoring_prompt:
            monitoring_prompt = \
        "Critisize the above Action Input and show your work."+\
        " Without additionnal information.\nCritique:"
        super().__init__(
            hybridstore = hybridstore,
            llm = llm,
            program_key = program_key,
            prompt = prompt,
            monitoring_prompt = monitoring_prompt,
            max_prompt_tokens = max_prompt_tokens,
            language = language,
            monitoring = monitoring,
            verbose = verbose
        )

        update_objective_tool = Tool(
            name="UpdateObjective",
            description=\
    """
    Usefull to update your long-term objective
    The Input should be the new objective
    """,
            func=self.update_objective
        )

        read_tools_instructions = Tool(
            name = "ReadToolsInstructions",
            description = \
    """
    Usefull to read the tools instructions
    No Input needed
    """,
            func=self.read_tools_instructions
        )

        tools.append(update_objective_tool)
        tools.append(read_tools_instructions)

        self.tools_instructions = "You have access to the following tools:\n"
        for tool in tools:
            self.tools_instructions += f"\n{tool.name}:{tool.description}"
            self.allowed_tools.append(tool.name)
            self.tools_map[tool.name] = tool
        self.clear()

    def update_objective(self, objective:str):
        self.objective = objective
        return "Objective sucessfully updated"

    def read_tools_instructions(self):
        return self.tools_instructions

    def get_program_trace(self, prompt:str):
        program_trace = (self.program_trace+"\n"+prompt).format(
            language=self.language
        )
        temp = self.prompt.format(
            objective=self.objective,
            program_trace=program_trace,
            language=self.language
        )
        num_tok = self.llm.get_num_tokens(temp)
        if num_tok > self.max_prompt_tokens:
            program_trace = self.program_trace[num_tok-self.max_prompt_tokens:]+prompt
        else:
            program_trace = self.program_trace+prompt
        return program_trace

    def get_current_program(self) -> Optional[Graph]:
        """Method to retreive the current program from the stack"""
        if len(self.program_stack) > 0:
            return self.program_stack[len(self.program_stack)-1]
        return None
    
    def call_subprogram(self, node:Node):
        """Method to call a sub-program"""
        purpose = node.properties["name"]
        program = node.properties["program"]
        self.update(f"Start Sub-Program: {program}\nSub-Program Purpose: {purpose}")
        self.execute_program(program)
        self.update(f"End SubProgram: {program}")

    def get_next(self, node:Node) -> Optional[Node]:
        """Method to get the next node"""
        name = node.properties["name"]
        result = self.get_current_program().query(
            'MATCH ({name:"'+name+'"})-[:NEXT]->(n) RETURN n'
        )
        if len(result.result_set) > 0:
            return result.result_set[0][0]
        return None

    def predict(self, prompt:str, **kwargs) -> str:
        """Predict the next words using the program context"""
        template = self.prompt.format(
            objective=self.objective,
            program_trace=self.get_program_trace(prompt),
        )
        return super().predict(template, language=self.language, **kwargs)

    def execute_program(self, program_index:str):
        """Method to execute a program"""
        program = Graph(program_index, self.hybridstore.client)
        self.program_stack.append(program)
        result = self.get_current_program().query(
            'MATCH (n:Control {name:"Start"}) RETURN n'
        )
        if len(result.result_set) == 0:
            raise ValueError("No entry point in the program")
        if len(result.result_set) > 1:
            raise ValueError("Multiple entry point in the program")
        starting_node = result.result_set[0][0]
        current_node = self.get_next(starting_node)
        next_node = None
        iteration = 0
        while True:
            if current_node.label == "Program":
                self.call_subprogram(current_node)
                next_node = self.get_next(current_node)
            elif current_node.label == "Action":
                self.use_tool(current_node)
                next_node = self.get_next(current_node)
                if self.monitoring:
                    self.monitor()
            elif current_node.label == "Decision":
                next_node = self.decide_next(current_node)
            elif current_node.label == "Control":
                if current_node.properties["name"] == "End":
                    break
            else:
                raise RuntimeError(
                    "Invalid label for node."+
                    " Please verify your programs using RedisInsight."
                )
            if next_node is None:
                raise RuntimeError(
                    "Program failed after reaching a non-terminated path."+
                    " Please verify your programs using RedisInsight."
                )
            current_node = next_node
            iteration += 1
            if iteration > self.max_iterations:
                raise RuntimeError("Program failed after reaching max iteration")
        self.program_stack.pop()

    def decide_next(self, node:Node) -> Node:
        """Method to make a decision"""
        # get possible output options
        purpose = node.properties["name"]
        question = node.properties["question"]
        
        options = []
        result = self.get_current_program().query(
            'MATCH (n:Decision {name:"'+purpose+'"})-[r]->() RETURN type(r)'
        )
        for record in result.result_set:
            options.append(record[0])
        choice = " or ".join(options)
        prompt = \
f"""
Decision: {question}.
Decision Purpose: {purpose}.
Decision Answer (must be {choice}):"""
        if self.verbose:
            print(f"{Fore.GREEN}{prompt}{Style.RESET_ALL}")
        decision = self.predict_decision(
            self.get_program_trace(prompt),
            question,
            options
        )
        if self.verbose:
            print(f"{Fore.YELLOW}\n{decision}{Style.RESET_ALL}")
        self.update(prompt+decision)
        result = self.get_current_program().query(
            'MATCH (:Decision {name:"'+purpose+'"})-[:'+decision+']->(n) RETURN n'
        )
        next_node = result.result_set[0][0]
        return next_node

    def use_tool(self, node:Node):
        """Method to use a tool"""
        purpose = node.properties["name"]
        tool_name = node.properties["tool"]
        if tool_name != "Predict":
            self.validate_tool(tool_name)
        tool_params_prompt = node.properties["params"]
        tool_prompt = \
f"""
Action: {tool_name}
Action Purpose: {purpose}
Action Input: {tool_params_prompt}
"""
        if self.verbose:
            print(f"{Fore.GREEN}{tool_prompt.format(language=self.language)}{Style.RESET_ALL}")
        if tool_name == "Predict":
            tool_input = tool_params_prompt
            observation = self.predict(tool_prompt)
            final_prompt = \
f"""
Action: {tool_name}
Action Purpose: {purpose}
Action Input: {tool_input}
{observation}
"""
            if self.verbose:
                print(f"{Fore.YELLOW}{observation}{Style.RESET_ALL}")
        else:
            tool_input = self.predict(tool_prompt)
            observation = self.execute_tool(tool_name, tool_input)
            final_prompt = \
f"""
Action: {tool_name}
Action Purpose: {purpose}
Action Input: {tool_input}
Action Observation: {observation}
"""
            if self.verbose:
                print(
                    f"{Fore.GREEN}Action Observation: "+
                    f"{Fore.BLUE}{observation}{Style.RESET_ALL}"
                )
        self.update(final_prompt)

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

    def update(self, prompt:str):
        """Method to update the program trace"""
        self.program_trace + "\n" + prompt

    def monitor(self):
        """Method to monitor the process"""
        critique = self.predict(self.monitoring_prompt)
        self.update(f"Monitoring: {critique}")

    def clear(self):
        """Method to clear the program trace"""
        self.program_trace = ""

    def run(self, objective:str):
        """Method to run the agent"""
        self.objective = objective
        self.clear()
        formated_prompt = self.prompt.format(
            language=self.language,
            objective=self.objective,
            program_trace=self.program_trace
        )
        formated_prompt = formated_prompt.replace("Objective:", f"Objective:{Fore.BLUE}")
        print(f"{Fore.GREEN}{formated_prompt}{Style.RESET_ALL}")
        self.execute_program(self.program_key)
        return "Program Sucessfully Executed"