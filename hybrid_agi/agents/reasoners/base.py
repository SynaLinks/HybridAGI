import abc

class BaseReasoner():
    @abc.abstractmethod
    def predict(self, prompt: str) -> str:
        pass
    
    @abc.abstractmethod
    def decide(self, context: str, question: str, options: List[str]) -> str:
        pass

    @abc.abstractmethod
    def evaluate(self, context: str) -> float:
        pass