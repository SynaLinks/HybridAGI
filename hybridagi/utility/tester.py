"""The program tester. Copyright (C) 2023 SynaLinks. License: GPL-3.0"""

from typing import List
from ..hybridstores.program_memory.program_memory import ProgramMemory

RESERVED_NAMES = [
    "main",
    "playground",
    "filesystem",
    "program_memory",
    "trace_memory",
    "\u006D\u0061\u0069\u006E",
    "\u0070\u006C\u0061\u0079\u0067\u0072\u006F\u0075\u006E\u0064",
    "\u0066\u0069\u006C\u0065\u0073\u0079\u0073\u0074\u0065\u006D",
    "\u0070\u0072\u006F\u0067\u0072\u0061\u006D\u005F\u006D\u0065\u006D\u006F\u0072\u0079",
    "\u0074\u0072\u0061\u0063\u0065\u005F\u006D\u0065\u006D\u006F\u0072\u0079",
]

FORBIDDEN_COMMANDS = [
    "DETACH",
    "DELETE",
    "SET",
    "WHEN",
    "WITH",
    "AS",
    "RETURN",
]

class TesterUtility():
    """The class to make some verification to graph programs"""
    program_memory: ProgramMemory
    program_name: str = ""

    class Config:
        """Configuration for this pydantic object."""
        arbitrary_types_allowed = True

    def is_protected(self, program_name: str):
        if program_name in RESERVED_NAMES:
            return True
        else:
            if self.program_memory.depends_on("main", program_name):
                return True
        return False

    def check_injection_attemp(self, program:str):
        for cmd in FORBIDDEN_COMMANDS:
            if cmd in program:
                raise RuntimeError("Error: Detected Cypher injection attemp")

    def load_program_into_playground(
            self,
            program_name: str,
            program: str):
        """Try to load a program into playground for testing"""
        try:
            self.program_memory.playground.delete()
        except Exception:
            pass
        try:
            self.program_memory.playground.query(program)
        except Exception as err:
            raise RuntimeError(
                f"Error while loading '{program_name}': {err}. "+\
                "Please change your program")
        self.program_name = program_name

    def check_protected_program(self, program_name: str):
        """Check if the system try to modify a protected program"""
        if self.is_protected(program_name):
            raise RuntimeError(
                f"Error while loading '{program_name}': "+\
                "Trying to modify a protected program. "+\
                "Change the name of the program")

    def check_starting_node_count(self):
        """Check how many starting node the program have"""
        result = self.program_memory.playground.query(
            'MATCH (n:Control {name:"Start"}) RETURN n')
        if len(result) == 0:
            raise RuntimeError(
                f"Error while loading '{self.program_name}': "+\
                "No starting node detected, please "+\
                "make sure to start your program correctly")
        if len(result) > 1:
            raise RuntimeError(
                f"Error while loading '{self.program_name}': "+\
                "Starting node is connected to more than one node "+\
                "make sure to start your program correctly")

    def check_ending_node_count(self):
        """Check how many ending node the program have"""
        result = self.program_memory.playground.query(
            'MATCH (n:Control {name:"End"}) RETURN n')
        if len(result) == 0:
            raise RuntimeError(
                f"Error while loading '{self.program_name}': "+\
                "No ending node detected, please "+\
                "make sure to end your program correctly")
        if len(result) > 1:
            raise RuntimeError(
                f"Error while loading '{self.program_name}': "+\
                "Multiple ending point detected, "+
                "please correct your programs.")

    def check_starting_node_output(self):
        """Check starting node outgoing edges"""
        result = self.program_memory.playground.query(
            'MATCH (n:Control {name:"Start"})-[r]->(m) RETURN r')
        if len(result) == 0:
            raise RuntimeError(
                f"Error while loading '{self.program_name}': "+\
                "Starting node is not connected (meaning it doesn't have outgoing edge) "+\
                "make sure to start your program correctly")
        if len(result) > 1:
            raise RuntimeError(
                f"Error while loading '{self.program_name}': "+\
                "Starting node is connected to more than one node "+\
                "make sure to start your program correctly")

    def check_starting_node_input(self):
        """Check starting node incoming edges"""
        result = self.program_memory.playground.query(
            'MATCH (m)-[r]->(n:Control {name:"Start"}) RETURN r')
        if len(result) > 0:
            raise RuntimeError(
                f"Error while loading '{self.program_name}': "+\
                "Starting node cannot have incoming edges "+\
                "make sure to start your program correctly")

    def check_ending_node_input(self):
        """Check ending node incoming edges"""
        result = self.program_memory.playground.query(
            'MATCH (m)-[r]->(n:Control {name:"End"}) RETURN r')
        if len(result) == 0:
            raise RuntimeError(
                f"Error while loading '{self.program_name}': "+\
                "Ending node should at least have one incoming edge"+\
                "make sure to end your program correctly")

    def check_ending_node_output(self):
        """Check ending node outgoing edges"""
        result = self.program_memory.playground.query(
            'MATCH (n:Control {name:"End"})-[r]->(m) RETURN r')
        if len(result) > 0:
            raise RuntimeError(
                f"Error while loading '{self.program_name}': "+\
                "Ending node cannot have outgoing edges"+\
                "make sure to end your program correctly")

    def check_program_dependencies(self):
        result = self.program_memory.playground.query(
            'MATCH (p:Program) RETURN p.program AS program')
        for record in result:
            subprogram = record[0]
            if self.is_protected(subprogram):
                raise RuntimeError(
                    f"Error while loading '{self.program_name}'. "+\
                    f"Trying to call a protected program '{subprogram}'. Try to remove it")
            if not self.program_memory.exists(subprogram):
                raise RuntimeError(
                    f"Error while loading '{self.program_name}': "+\
                    f"The sub-program '{subprogram}' does not exist. "+\
                    "Please correct your program")
                
    def verify_programs(
            self,
            names: List[str],
            programs: List[str]):
        """Verify programs"""
        for idx, program in enumerate(programs):
            program_name = names[idx]
            self.check_protected_program(program_name)
            self.check_injection_attemp(program)

            self.load_program_into_playground(
                program_name,
                program)
            
            self.check_starting_node_count()
            self.check_starting_node_input()
            self.check_starting_node_output()

            self.check_ending_node_count()
            self.check_ending_node_input()
            self.check_ending_node_output()

            self.check_program_dependencies()