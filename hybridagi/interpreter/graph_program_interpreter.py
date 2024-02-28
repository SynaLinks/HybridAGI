"""The graph program interpreter. Copyright (C) 2023 SynaLinks. License: GPL-3.0"""

import random
from collections import deque
from typing import Dict, List, Optional, Iterable, Callable
from colorama import Fore, Style

from falkordb import Node
from ..hybridstores.hybridstore import KnowledgeGraph

from langchain.tools import BaseTool, Tool
from langchain.base_language import BaseLanguageModel

from ..hybridstores.program_memory.program_memory import ProgramMemory
from ..hybridstores.trace_memory.trace_memory import TraceMemory

from ..toolkits.base import BaseToolKit
from ..toolkits.trace_memory_toolkit import TraceMemoryToolKit
from ..toolkits.program_memory_toolkit import ProgramMemoryToolKit
from ..parsers.file import FileOutputParser
from ..reasoners.ranked_action_reasoner import RankedActionReasoner

from ..parsers.program_name import ProgramNameOutputParser

class GraphProgramInterpreter(RankedActionReasoner):
    """LLM based interpreter for graph programs"""
    program_memory: ProgramMemory
    trace_memory: TraceMemory
    smart_llm: BaseLanguageModel
    fast_llm: BaseLanguageModel
    program_name: str = ""
    program_stack: Iterable = deque()
    current_node_stack: Iterable = deque()
    tools: List[BaseTool] = []
    toolkits: List[BaseToolKit] = []
    tools_map: Dict[str, BaseTool] = {}
    max_decision_attemps: int = 5
    max_evaluation_attemps: int = 5
    current_iteration:int = 0
    max_iteration: int = 50
    smart_llm_max_token: int = 4000
    fast_llm_max_token: int = 4000
    verbose: bool = True
    debug: bool = False
    program_name_parser: ProgramNameOutputParser = ProgramNameOutputParser()
    
    def __init__(
            self,
            program_memory: ProgramMemory,
            trace_memory: TraceMemory,
            smart_llm: BaseLanguageModel,
            fast_llm: BaseLanguageModel,
            program_name: str = "main",
            tools: List[BaseTool] = [],
            toolkits: List[BaseToolKit] =  [],
            smart_llm_max_token: int = 4000,
            fast_llm_max_token: int = 4000,
            max_decision_attemps:int = 5,
            max_evaluation_attemps:int = 5,
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

        trace_memory_toolkit = TraceMemoryToolKit(
            trace_memory = trace_memory,
        )

        program_memory_toolkit = ProgramMemoryToolKit(
            program_memory = program_memory,
        )

        toolkits.append(trace_memory_toolkit)
        toolkits.append(program_memory_toolkit)

        predict_tool = Tool(
            name = "Predict",
            description = "Usefull for intermediate reasoning steps."+\
                "The Input should be the Prompt used.",
            func=self.predict_tool)

        call_program_tool = Tool(
            name = "CallProgram",
            description = "Usefull to call a subprogram dynamically. "+\
                "The Input should be the name of the program",
            func=self.call_program_tool)

        plannify_tool = Tool(
            name = "Plannify",
            description = "Usefull to plan a workflow of programs. "+\
                "The Input should be the Cypher program to execute.",
            func=self.plannify_tool)

        tools.append(predict_tool)
        tools.append(call_program_tool)
        tools.append(plannify_tool)

        for toolkit in toolkits:
            tools += toolkit.tools

        tools_map = {}
        for tool in tools:
            tools_map[tool.name] = tool

        super().__init__(
            program_memory = program_memory,
            trace_memory = trace_memory,
            smart_llm = smart_llm,
            fast_llm = fast_llm,
            smart_llm_max_token = smart_llm_max_token,
            fast_llm_max_token = fast_llm_max_token,
            program_name = program_name,
            tools = tools,
            toolkits = toolkits,
            tools_map = tools_map,
            max_decision_attemps = max_decision_attemps,
            max_evaluation_attemps = max_evaluation_attemps,
            max_iteration = max_iteration,
            verbose = verbose,
            debug = debug,
            pre_decision_callback = pre_decision_callback,
            post_decision_callback = post_decision_callback,
            pre_action_callback = pre_action_callback,
            post_action_callback = post_action_callback,
        )
    
    def predict_tool(self, prediction: str):
        return prediction

    def call_program_tool(self, program_name: str):
        program_name = self.program_name_parser.parse(program_name)
        try:
            exists = self.program_memory.exists(program_name)
            if not exists:
                return f"Error while calling '{program_name}': This program does not exist"
        except Exception:
            return "Invalid program name: Please correct yourself"
        if self.program_memory.program_tester.is_protected(program_name):
            return f"Error while calling '{program_name}': Trying to call a protected program"
        self.call_program_by_name(program_name)
        return f"Successfully called '{program_name}' program"

    def plannify_tool(self, program: str):
        file_parser = FileOutputParser()
        filenames, contents, _ = file_parser.parse(program)
        program_name = self.program_name_parser.parse(filenames[0])
        program = contents[0]
        if len(filenames) > 1:
            return f"Error occured while loading '{program_name}': "+\
                "More than one Cypher program detected"
        self.program_memory.program_tester.verify_programs(
            [program_name],
            [program])
        self.program_memory.add_programs(
            [program_name],
            [program])
        self.call_program_by_name(program_name)
        return f"Successfully planned '{program_name}'"

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

    def call_program_by_name(self, program_name: str):
        if self.program_memory.exists(program_name):
            if self.program_memory.program_tester.is_protected(program_name):
                return f"Error occured while calling '{program_name}': "+\
                    "Trying to call a protected program"
        else:
            result = self.program_memory.similarity_search(program_name, k=1)
            if len(result) > 0:
                most_similar_name = result[0]
                return f"Error occured while calling '{program_name}': "+\
                    f"Not existing, do you mean '{most_similar_name}'?"
            return f"Error occured while calling '{program_name}': "+\
                    "Not existing, please correct the program name"
        self.set_current_node(self.get_next(self.get_current_node()))
        program = self.program_memory.create_graph(program_name)
        self.program_stack.append(program)
        starting_node = self.get_starting_node(program_name)
        self.current_node_stack.append(starting_node)

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
    
    def set_current_node(self, node: Node):
        """Method to set the current node from the stack"""
        if len(self.current_node_stack) > 0:
            self.current_node_stack[-1] = node

    def call_program_node(self, node: Node):
        """Method to call a program"""
        purpose = node.properties["name"]
        program_name = node.properties["program"]
        self.trace_memory.commit_program_start(
            purpose = purpose,
            program_name = program_name,
        )
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
            self.trace_memory.commit_program_end(
                program_name = ending_program_name)
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
            'MATCH (n:Decision {name:"'+purpose+'"})-[r]->() RETURN type(r)')
        for record in result:
            options.append(record[0])
        random.shuffle(options)
        decision = self.perform_decision(purpose, question, options)
        result = self.get_current_program().query(
            'MATCH (:Decision {name:"'+purpose+'"})-[:'+decision+']->(n) RETURN n')
        next_node = result[0][0]
        return next_node

    def use_tool(self, node:Node) -> Node:
        """Method to use a tool"""
        try:
            purpose = node.properties["name"]
            tool_name = node.properties["tool"]
        except Exception:
            raise RuntimeError(
                "Every Action Node should have a name and tool parameter, please verify '"
                +self.get_current_program().index_name+"' program")
        if "prompt" in node.properties:
            tool_input_prompt = node.properties["prompt"]
        else:
            tool_input_prompt = ""
        disable_inference = False
        if "disable_inference" in node.properties:
            disable = node.properties["disable_inference"]
            disable_inference = (disable.lower() == "true")

        ranked_inferences = 1
        if "ranked_inferences" in node.properties:
            nb_ranked_inferences = node.properties["ranked_inferences"]
            ranked_inferences = int(nb_ranked_inferences)
        
        self.perform_action(
            purpose,
            tool_name,
            tool_input_prompt,
            disable_inference = disable_inference,
            ranked_inferences = ranked_inferences,
        )
        
        return self.get_next(self.get_current_node())

    def run_step(self) -> Optional[Node]:
        """Run a single step of the program"""
        current_node = self.get_current_node()
        next_node = None
        self.current_iteration += 1
        if self.current_iteration > self.max_iteration:
            raise RuntimeError("Program failed after reaching max iteration")
        if current_node.label == "Program":
            next_node = self.call_program_node(current_node)
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
            raise RuntimeError(
                "Invalid Node label used, should be Control, Action, Decision or Program, please verify '"
                +self.get_current_program().index_name+"' program")
        if next_node is not None:
            self.set_current_node(next_node)
        return next_node

    async def async_decide_next(self, node:Node) -> Node:
        """Method to make a decision"""
        purpose = node.properties["name"]
        question = node.properties["question"]

        options = []
        result = self.get_current_program().query(
            'MATCH (n:Decision {name:"'+purpose+'"})-[r]->() RETURN type(r)')
        for record in result:
            options.append(record[0])

        decision = await self.async_perform_decision(purpose, question, options)
        result = self.get_current_program().query(
            'MATCH (:Decision {name:"'+purpose+'"})-[:'+decision+']->(n) RETURN n')
        next_node = result[0][0]
        return next_node

    async def async_use_tool(self, node:Node) -> Node:
        """Method to use a tool"""
        purpose = node.properties["name"]
        tool_name = node.properties["tool"]
        tool_input_prompt = node.properties["prompt"]

        disable_inference = False
        if "disable_inference" in node.properties:
            disable = node.properties["disable_inference"]
            disable_inference = (disable.lower() == "true")

        ranked_inferences = 1
        if "ranked_inferences" in node.properties:
            nb_ranked_inferences = node.properties["ranked_inferences"]
            ranked_inferences = int(nb_ranked_inferences)
        
        await self.async_perform_action(
            purpose,
            tool_name,
            tool_input_prompt,
            disable_inference = disable_inference,
            ranked_inferences = ranked_inferences,
        )
        return self.get_next(self.get_current_node())

    async def async_run_step(self) -> Optional[Node]:
        """Run a single step of the program"""
        current_node = self.get_current_node()
        next_node = None
        self.current_iteration += 1
        if self.current_iteration > self.max_iteration:
            raise RuntimeError("Program failed after reaching max iteration")
        if current_node.label == "Program":
            next_node = self.call_program_node(current_node)
        elif current_node.label == "Action":
            next_node = await self.async_use_tool(current_node)
        elif current_node.label == "Decision":
            next_node = await self.async_decide_next(current_node)
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
        self.trace_memory.start_new_trace()
        self.trace_memory.update_objective("N/A")

    def start(self, objective: str):
        """Start the agent"""
        if self.verbose:
            print(f"{Fore.GREEN}[!] Starting the interpreter{Style.RESET_ALL}")
        self.trace_memory.update_objective(objective)
        self.current_iteration = 0
        self.trace_memory.start_new_trace()
        self.trace_memory.commit_program_start(
            purpose = objective,
            program_name = self.program_name,
        )
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
    
    async def async_run(self, objective: str):
        """Method to run the agent"""
        self.start(objective)
        while not self.finished():
            await self.async_run_step()
        if self.verbose:
            print(f"{Fore.GREEN}[!] Program Successfully Executed{Style.RESET_ALL}")
        return "Program Successfully Executed"
