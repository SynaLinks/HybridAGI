"""The graph program interpreter. Copyright (C) 2023 SynaLinks. License: GPL-3.0"""

from collections import deque
from typing import List, Optional, Iterable, Callable
from colorama import Fore, Style

from redisgraph import Node

from hybridagikb import KnowledgeGraph

from langchain.tools import BaseTool, Tool
from langchain.base_language import BaseLanguageModel
from ..hybridstores.program_memory.program_memory import ProgramMemory
from ..reasoners.base import BaseReasoner
from .base import BaseGraphProgramInterpreter

COLORS = [f"{Fore.BLUE}", f"{Fore.MAGENTA}"]

class GraphProgramInterpreter(BaseGraphProgramInterpreter):
    """LLM based interpreter for graph programs"""
    program_memory: ProgramMemory
    smart_llm: BaseLanguageModel
    fast_llm: BaseLanguageModel
    program_name: str = ""
    program_stack: Iterable = deque()
    current_node_stack: Iterable = deque()
    reasoners: List[BaseReasoner] = []
    max_decision_attemp: int = 5
    current_iteration:int = 0
    max_iteration: int = 50
    smart_llm_max_token: int = 4000
    fast_llm_max_token: int = 4000
    verbose: bool = True
    debug: bool = False
    
    def __init__(
            self,
            program_memory: ProgramMemory,
            smart_llm: BaseLanguageModel,
            fast_llm: BaseLanguageModel,
            program_name: str = "main",
            tools: List[BaseTool] = [],
            reasoners: List[BaseReasoner] =  [],
            smart_llm_max_token: int = 4000,
            fast_llm_max_token: int = 4000,
            max_decision_attemp:int = 5,
            max_iteration:int = 50,
            verbose: bool = True,
            debug: bool = False,
            pre_decision_callback: Optional[Callable[
                [str, str, List[str]],
                None
            ]] = None,
            post_decision_callback: Optional[Callable[
                [str, str, List[str], str],
                None
            ]] = None,
            pre_action_callback: Optional[Callable[
                [str, str, str],
                None
            ]] = None,
            post_action_callback: Optional[Callable[
                [str, str, str, str],
                None
            ]] = None):

        update_objective_tool = Tool(
            name = "UpdateObjective",
            description = \
    """
    Usefull to update your long-term objective
    The Input should be the new objective
    """,
            func=self.update_objective_tool)

        update_note_tool = Tool(
            name = "UpdateNote",
            description = \
    """
    Usefull to update your notes
    The Input should be the new note
    """,
            func=self.update_note_tool)

        clear_trace_tool = Tool(
            name = "ClearTrace",
            description = \
    """
    Usefull to clean up the working memory
    No Input needed (should be N/A)
    """,
            func=self.clear_trace_tool)

        revert_trace_tool = Tool(
            name = "RevertTrace",
            description = \
    """
    Usefull to correct your last actions
    The Input should be the number of steps to revert
    """,
            func=self.revert_trace_tool)

        call_program_tool = Tool(
            name = "CallProgram",
            description = \
    """
    Usefull to call a subprogram dynamically
    The Input should be the name of the program
    """,
            func=self.call_program_tool)

        tools.append(update_objective_tool)
        tools.append(update_note_tool)
        tools.append(revert_trace_tool)
        tools.append(call_program_tool)
        tools.append(clear_trace_tool)

        for reasoner in reasoners:
            tools += reasoner.tools

        tools_map = {}
        for tool in tools:
            tools_map[tool.name] = tool

        super().__init__(
            program_memory = program_memory,
            smart_llm = smart_llm,
            fast_llm = fast_llm,
            smart_llm_max_token = smart_llm_max_token,
            fast_llm_max_token = fast_llm_max_token,
            program_name = program_name,
            reasoners = reasoners,
            tools_map = tools_map,
            max_decision_attemp = max_decision_attemp,
            max_iteration = max_iteration,
            verbose = verbose,
            debug = debug,
            pre_decision_callback = pre_decision_callback,
            post_decision_callback = post_decision_callback,
            pre_action_callback = pre_action_callback,
            post_action_callback = post_action_callback)

    def get_starting_node(self, program_name: str):
        program = self.program_memory.create_graph(program_name)
        result = program.query(
            'MATCH (n:Control {name:"Start"}) RETURN n')
        if len(result) == 0:
            raise RuntimeError("No entry point detected,"+
                " please make sure you loaded the programs.")
        if len(result) > 1:
            raise RuntimeError("Multiple entry point detected,"+
                " please correct your programs.")
        starting_node = result[0][0]
        return starting_node

    def update_objective_tool(self, objective: str):
        self.working_memory.update_objective(objective)
        return "Objective sucessfully updated"

    def update_note_tool(self, note: str):
        self.working_memory.update_note(note)
        return "Note sucessfully updated"

    def revert_trace_tool(self, n_steps: str):
        n = int(n_steps)
        self.working_memory.revert(n)
        return f"Successfully reverted {n} steps"

    def clear_trace_tool(self, _):
        self.working_memory.clear()
        return "Working memory cleaned sucessfully"

    def call_program_tool(self, program_name: str):
        if program_name == "main" or self.program_memory.depends_on("main", program_name):
            return f"Error occured while calling '{program_name}': "+\
                "Trying to call a protected program"
        program_name = program_name.strip().lower().replace(" ", "_")
        if not self.program_memory.exists(program_name):
            return f"Error occured while calling '{program_name}': "+\
                "Not existing, please verify that you have the correct name"
        self.set_current_node(self.get_next(self.get_current_node()))
        program = self.program_memory.create_graph(program_name)
        self.program_stack.append(program)
        starting_node = self.get_starting_node(program_name)
        self.current_node_stack.append(starting_node)
        return f"Successfully called '{program_name}' program"

    def get_current_program(self) -> Optional[KnowledgeGraph]:
        """Method to retreive the current program from the stack"""
        if len(self.program_stack) > 0:
            return self.program_stack[-1]
        return None

    def get_current_node(self) -> Optional[Node]:
        """Method to retreive the current node from the stack"""
        if len(self.current_node_stack) > 0:
            return self.current_node_stack[-1]
        return None
    
    def set_current_node(self, node):
        """Method to set the current node from the stack"""
        if len(self.current_node_stack) > 0:
            self.current_node_stack[-1] = node

    def call_program(self, node: Node):
        """Method to call a program"""
        purpose = node.properties["name"]
        program_name = node.properties["program"]
        self.working_memory.update_trace(
            f"Start Sub-Program: {program_name}\nSub-Program Purpose: {purpose}"
        )
        if self.verbose:
            print(COLORS[self.current_iteration%2])
            print(f"Start Sub-Program: {program_name}")
            print(f"Sub-Program Purpose: {purpose}{Style.RESET_ALL}")
        program = self.program_memory.create_graph(program_name)
        self.program_stack.append(program)
        starting_node = self.get_starting_node(program_name)
        self.current_node_stack.append(self.get_next(starting_node))
        return self.get_current_node()

    def end_current_program(self):
        """Method to end the current program"""
        ending_program = self.program_stack.pop()
        self.current_node_stack.pop()
        if ending_program is not None:
            ending_program_name = ending_program.name
            self.working_memory.update_trace(f"End Sub-Program: {ending_program_name}")
            if self.get_current_node() is not None:
                return self.get_next(self.get_current_node())
        return None

    def get_next(self, node:Node) -> Optional[Node]:
        """Method to get the next node"""
        name = node.properties["name"]
        result = self.get_current_program().query(
            'MATCH ({name:"'+name+'"})-[:NEXT]->(n) RETURN n')
        if len(result) > 0:
            return result[0][0]
        return None

    def decide_next(self, node:Node) -> Node:
        """Method to make a decision"""
        purpose = node.properties["name"]
        question = node.properties["question"]

        options = []
        result = self.get_current_program().query(
            'MATCH (n:Decision {name:"'+purpose+'"})-[r]->() RETURN type(r)'
        )
        for record in result:
            options.append(record[0])

        decision = self.perform_decision(purpose, question, options)

        if self.verbose:
            decision_template = \
            f"Decision Purpose: {purpose}" + \
            f"\nDecision: {question}" + \
            f"\nDecision Answer: {decision}"
            print(COLORS[self.current_iteration%2])
            print(f"{decision_template}{Style.RESET_ALL}")

        result = self.get_current_program().query(
            'MATCH (:Decision {name:"'+purpose+'"})-[:'+decision+']->(n) RETURN n')
        next_node = result[0][0]
        return next_node

    def use_tool(self, node:Node):
        """Method to use a tool"""
        purpose = node.properties["name"]
        tool_name = node.properties["tool"]
        tool_input_prompt = node.properties["prompt"]

        disable_inference = False
        if "disable_inference" in node.properties:
            disable = node.properties["disable_inference"]
            disable_inference = (disable.lower() == "true")
        
        action = self.perform_action(
            purpose,
            tool_name,
            tool_input_prompt,
            disable_inference = disable_inference)
        
        if self.verbose:
            print(COLORS[self.current_iteration%2])
            print(f"{action}{Style.RESET_ALL}")
        self.working_memory.update_trace(action)
        return self.get_next(self.get_current_node())

    def run_step(self) -> Optional[Node]:
        """Run a single step of the program"""
        current_node = self.get_current_node()
        next_node = None
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
                    " Please verify your programs using RedisInsight.")
        else:
            node_name = current_node.properties["name"]
            raise RuntimeError(
                f"Invalid label for node '{node_name}'."+
                " Please verify your programs using RedisInsight.")
        if next_node is not None:
            self.set_current_node(next_node)
        return next_node

    def finished(self):
        """Check if the run is finished"""
        return self.get_current_node() is None

    def stop(self):
        """Stop the agent"""
        self.current_node_stack = deque()
        self.program_stack = deque()
        self.working_memory.clear()
        self.working_memory.update_objective("N/A")

    def start(self, objective: str):
        """Start the agent"""
        self.working_memory.update_objective(objective)
        self.current_iteration = 0
        self.working_memory.clear()
        program = self.program_memory.create_graph(self.program_name)
        self.program_stack.append(program)
        starting_node = self.get_starting_node(self.program_name)
        self.current_node_stack.append(self.get_next(starting_node))
    
    def run(self, objective: str):
        """Method to run the agent"""
        self.start(objective)
        while not self.finished():
            self.run_step()
        if self.verbose:
            print(f"{Fore.GREEN}[!] Program Successfully Executed{Style.RESET_ALL}")
        return "Program Successfully Executed"