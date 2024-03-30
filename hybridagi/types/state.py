from collections import deque
from falkordb import Node, Graph
from typing import List, Iterable, Optional, Tuple
from hybridagi import FileSystemContext

class AgentState():

    def __init__(self):
        self.init()

    def get_current_program(self) -> Optional[Graph]:
        """Method to retreive the current program from the stack"""
        if len(self.program_stack) > 0:
            return self.program_stack[-1][1]
        return None

    def get_current_node(self) -> Optional[Node]:
        """Method to retreive the current node from the stack"""
        if len(self.program_stack) > 0:
            return self.program_stack[-1][0]
        return None
    
    def set_current_node(self, node: Node):
        """Method to set the current node from the stack"""
        if len(self.program_stack) > 0:
            _, program = self.program_stack[-1]
            self.program_stack[-1] = (node, program)

    def call_program(self, starting_node: Node, program: Graph):
        """Append the program stack"""
        self.program_stack.append((starting_node, program))

    def end_program(self) -> Optional[Graph]:
        """Pop the program stack"""
        _, program = self.program_stack.pop()
        return program

    def init(self):
        self.objective = "N/A"
        self.current_hop = 0
        self.program_trace = []
        self.program_stack = deque()
        self.filesystem_context = FileSystemContext()