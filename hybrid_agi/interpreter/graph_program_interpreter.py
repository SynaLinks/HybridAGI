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
from langchain.schema import BaseMemory

from hybrid_agi.interpreter.program_trace_memory import ProgramTraceMemory
from hybrid_agi.interpreter.base import BaseGraphProgramInterpreter

class GraphProgramInterpreter(BaseGraphProgramInterpreter):
    """LLM based interpreter for graph programs"""
    hybridstore: RedisGraphHybridStore
    llm: BaseLanguageModel
    memory: ProgramTraceMemory = ProgramTraceMemory()
    program_key: str = ""
    prompt: str = ""
    program_stack: Iterable = deque()
    max_iterations: int = 100
    max_tokens: int = 3000
    tools_instructions: str = ""
    verbose: bool = True
    debug: bool = False

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
            max_tokens = 4000,
            max_decision_attemps:int = 5,
            max_iterations:int = 100,
            monitoring: bool = False,
            verbose: bool = True,
            debug: bool = False,
        ):
        if program_key == "":
            program_key = hybridstore.main.name

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

        allowed_tools = []
        tools_map = {}
        tools_instructions = "You have access to the following tools:\n"
        for tool in tools:
            tools_instructions += f"\n{tool.name}:{tool.description}"
            allowed_tools.append(tool.name)
            tools_map[tool.name] = tool

        super().__init__(
            llm = llm,
            hybridstore = hybridstore,
            program_key = program_key,
            prompt = prompt,
            allowed_tools = allowed_tools,
            tools_map = tools_map,
            max_tokens = max_tokens,
            max_decision_attemps = max_decision_attemps,
            max_iterations = max_iterations,
            tools_instructions = tools_instructions,
            verbose = verbose,
            debug = debug
        )

    def update_objective(self, objective:str):
        self.memory.update_objective(objective)
        return "Objective sucessfully updated"

    def read_tools_instructions(self):
        return self.tools_instructions

    def get_current_program(self) -> Optional[Graph]:
        """Method to retreive the current program from the stack"""
        if len(self.program_stack) > 0:
            return self.program_stack[len(self.program_stack)-1]
        return None

    def call_subprogram(self, node:Node):
        """Method to call a sub-program"""
        purpose = node.properties["name"]
        program_name = node.properties["program"]
        program_key = self.hybridstore.program_key+":"+program_name
        self.memory.update_trace(f"Start Sub-Program: {program_name}\nSub-Program Purpose: {purpose}")
        self.execute_program(program_key)
        self.memory.update_trace(f"End SubProgram: {program_name}")

    def get_next(self, node:Node) -> Optional[Node]:
        """Method to get the next node"""
        name = node.properties["name"]
        result = self.get_current_program().query(
            'MATCH ({name:"'+name+'"})-[:NEXT]->(n) RETURN n'
        )
        if len(result.result_set) > 0:
            return result.result_set[0][0]
        return None

    def execute_program(self, program_index:str):
        """Method to execute a program"""
        program = Graph(program_index, self.hybridstore.client)
        self.program_stack.append(program)
        result = self.get_current_program().query(
            'MATCH (n:Control {name:"Start"}) RETURN n'
        )
        if len(result.result_set) == 0:
            raise ValueError("No entry point in the program,"+
                " please make sure you loaded the programs."
            )
        if len(result.result_set) > 1:
            raise ValueError("Multiple entry point in the program,"+
                " correct your programs"
            )
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
        purpose = node.properties["name"]
        question = node.properties["question"]

        options = []
        result = self.get_current_program().query(
            'MATCH (n:Decision {name:"'+purpose+'"})-[r]->() RETURN type(r)'
        )
        for record in result.result_set:
            options.append(record[0])

        context = self.prompt.format(
            program_trace=self.memory.get_trace(self.max_tokens)
        )

        decision = self.perform_decision(
            context,
            purpose,
            question,
            options
        )

        if self.verbose:
            decision_template = \
            f"Decision Purpose: {purpose}" + \
            f"\nDecision: {question}" + \
            f"\nDecision Answer: {decision}"
            print(
                f"{Fore.GREEN}{decision_template}{Style.RESET_ALL}")

        result = self.get_current_program().query(
            'MATCH (:Decision {name:"'+purpose+'"})-[:'+decision+']->(n) RETURN n'
        )
        next_node = result.result_set[0][0]
        return next_node

    def use_tool(self, node:Node):
        """Method to use a tool"""
        purpose = node.properties["name"]
        tool_name = node.properties["tool"]
        tool_input_prompt = node.properties["params"]

        context = self.prompt.format(
            program_trace=self.memory.get_trace(self.max_tokens)
        )
        action = self.perform_action(
            context,
            purpose,
            tool_name,
            tool_input_prompt
        )
        if self.verbose:
            print(f"{Fore.MAGENTA}{action}{Style.RESET_ALL}")
        self.memory.update_trace(action)

    def run(self, objective:str):
        """Method to run the agent"""
        self.memory.update_objective(objective)
        self.execute_program(self.program_key)
        return "Program Sucessfully Executed"