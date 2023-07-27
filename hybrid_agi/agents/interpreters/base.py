import abc
from hybrid_agi.agents.reasoners.base import BaseReasoner
from redisgraph import Node, Graph

class BaseGraphProgramInterpreter(BaseReasoner):
    """The base graph program interpreter"""

    @abc.abstractmethod
    def update(self, prompt:str):
        pass

    @abc.abstractmethod
    def update_objective(self, objective:str):
        pass

    @abc.abstractmethod
    def call_subprogram(self, node: Node):
        pass

    @abc.abstractmethod
    def execute_program(self, graph: Graph):
        pass

    @abc.abstractmethod
    def get_next(self, node: Node) -> Optional[Node]:
        pass

    @abc.abstractmethod
    def decide_next(self, node: Node) -> Optional[Node]:
        pass

    @abc.abstractmethod
    def act(self, node: Node):
        pass

    @abc.abstractmethod
    def monitor(self):
        pass

    @abc.abstractmethod
    def clear(self):
        pass

    @abc.abstractmethod
    def run(self, objective:str):
        pass