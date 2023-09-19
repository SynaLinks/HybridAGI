"""The graph program interpreter. Copyright (C) 2023 SynaLinks. License: GPL-3.0"""

from collections import deque
from typing import List, Optional, Iterable, Callable
from pydantic.v1 import BaseModel, Extra
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
    smart_llm: BaseLanguageModel
    fast_llm: BaseLanguageModel
    memory: ProgramTraceMemory = ProgramTraceMemory()
    program_index: str = ""
    program_stack: Iterable = deque()
    current_node_stack: Iterable = deque()
    max_decision_attemp: int = 5
    current_iteration:int = 0
    max_iteration: int = 50
    smart_llm_max_token: int = 4000
    fast_llm_max_token: int = 4000
    tools_instruction: str = ""
    verbose: bool = True
    debug: bool = False
    
    def __init__(
            self,
            hybridstore: RedisGraphHybridStore,
            smart_llm: BaseLanguageModel,
            fast_llm: BaseLanguageModel,
            program_index:str = "",
            tools:List[Tool] = [],
            smart_llm_max_token: int = 4000,
            fast_llm_max_token: int = 4000,
            max_decision_attemp:int = 5,
            max_iteration:int = 50,
            verbose: bool = True,
            debug: bool = False,
            pre_decision_callback: Optional[Callable[
                [str, str, str, List[str]],
                None
            ]] = None,
            post_decision_callback: Optional[Callable[
                [str, str, str, List[str], str],
                None
            ]] = None,
            pre_action_callback: Optional[Callable[
                [str, str, str, str],
                None
            ]] = None,
            post_action_callback: Optional[Callable[
                [str, str, str, str, str],
                None
            ]] = None,
        ):
        if program_index == "":
            program_index = hybridstore.main.name

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
        tools_instruction = "You have access to the following tools:\n"
        for tool in tools:
            tools_instruction += f"\n{tool.name}:{tool.description}"
            allowed_tools.append(tool.name)
            tools_map[tool.name] = tool

        super().__init__(
            hybridstore = hybridstore,
            smart_llm = smart_llm,
            fast_llm = fast_llm,
            smart_llm_max_token = smart_llm_max_token,
            fast_llm_max_token = fast_llm_max_token,
            program_index = program_index,
            allowed_tools = allowed_tools,
            tools_map = tools_map,
            max_decision_attemp = max_decision_attemp,
            max_iteration = max_iteration,
            verbose = verbose,
            debug = debug,
            pre_decision_callback = pre_decision_callback,
            post_decision_callback = post_decision_callback,
            pre_action_callback = pre_action_callback,
            post_action_callback = post_action_callback
        )

    def get_starting_node(self, program_index):
        program = Graph(program_index, self.hybridstore.client)
        result = program.query(
            'MATCH (n:Control {name:"Start"}) RETURN n'
        )
        if len(result.result_set) == 0:
            raise RuntimeError("No entry point detected,"+
                " please make sure you loaded the programs."
            )
        if len(result.result_set) > 1:
            raise RuntimeError("Multiple entry point detected,"+
                " please correct your programs."
            )
        starting_node = result.result_set[0][0]
        return starting_node

    def update_objective(self, objective:str):
        self.memory.update_objective(objective)
        return "Objective sucessfully updated"

    def read_tools_instructions(self, input:str):
        return self.tools_instructions

    def get_current_program(self) -> Optional[Graph]:
        """Method to retreive the current program from the stack"""
        if len(self.program_stack) > 0:
            return self.program_stack[-1]
        return None

    def get_current_node(self) -> Optional[Node]:
        if len(self.current_node_stack) > 0:
            return self.current_node_stack[-1]
        return None
    
    def set_current_node(self, node):
        if len(self.current_node_stack) > 0:
            self.current_node_stack[-1] = node

    def call_program(self, node: Node):
        """Method to call a program"""
        purpose = node.properties["name"]
        program_name = node.properties["program"]
        program_index = self.hybridstore.program_key+":"+program_name
        self.memory.update_trace(
            f"Start Sub-Program: {program_name}\nSub-Program Purpose: {purpose}"
        )
        program = Graph(program_index, self.hybridstore.client)
        self.program_stack.append(program)
        starting_node = self.get_starting_node(program_index)
        self.current_node_stack.append(self.get_next(starting_node))
        return self.get_current_node()

    def end_current_program(self):
        """Method to end the current program"""
        ending_program = self.program_stack.pop()
        self.current_node_stack.pop()
        if ending_program is not None:
            ending_program_name = \
            ending_program.name.replace(self.hybridstore.program_key+":", "")
            self.memory.update_trace(f"End Sub-Program: {ending_program_name}")
        return self.get_next(self.get_current_node())

    def get_next(self, node:Node) -> Optional[Node]:
        """Method to get the next node"""
        name = node.properties["name"]
        result = self.get_current_program().query(
            'MATCH ({name:"'+name+'"})-[:NEXT]->(n) RETURN n'
        )
        if len(result.result_set) > 0:
            return result.result_set[0][0]
        return None

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

        context = self.memory.get_trace(self.fast_llm_max_token)

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

        context = self.memory.get_trace(self.smart_llm_max_token)
        
        action = self.perform_action(
            context,
            purpose,
            tool_name,
            tool_input_prompt
        )
        if self.verbose:
            print(f"{Fore.MAGENTA}{action}{Style.RESET_ALL}")
        self.memory.update_trace(action)
        return self.get_next(self.get_current_node())

    def run_step(self) -> Optional[Node]:
        """Run a single step of the program"""
        current_node = self.get_current_node()
        next_node = None
        node_name = current_node.properties["name"]
        self.current_iteration += 1
        if self.current_iteration > self.max_iteration:
            raise RuntimeError("Program failed after reaching max iteration")
        if current_node.label == "Program":
            next_node = self.call_program(current_node)
        elif current_node.label == "Action":
            next_node = self.use_tool(current_node)
        elif current_node.label == "Decision":
            next_node = self.decide_next(current_node)
        elif current_node.label == "Control":
            if current_node.properties["name"] == "End":
                next_node = self.end_current_program()
            else:
                raise RuntimeError(
                    "Invalid name for control node."+
                    " Please verify your programs using RedisInsight."
                )
        else:
            raise RuntimeError(
                "Invalid label for node."+
                " Please verify your programs using RedisInsight."
            )
        self.set_current_node(next_node)
        return next_node

    def finished(self):
        """Check if the run is finished"""
        return self.get_current_node() is None

    def start(self, objective: str):
        """Start the agent"""
        self.update_objective(objective)
        self.current_iteration = 0
        self.memory.clear()
        program = Graph(self.program_index, self.hybridstore.client)
        self.program_stack.append(program)
        starting_node = self.get_starting_node(self.program_index)
        self.current_node_stack.append(self.get_next(starting_node))
    
    def run(self, objective: str):
        """Method to run the agent"""
        self.start(objective)
        while not self.finished():
            self.run_step()
        return "Program Sucessfully Executed"