import abc
from ...hybridstores.fact_memory.fact_memory import FactMemory

class KnowledgeParserBase():

    def __init__(
            self,
            fact_memory: FactMemory,
        ):
        self.fact_memory = fact_memory

    @abc.abstractmethod
    def parse(self, filename: str, content: str):
        pass
