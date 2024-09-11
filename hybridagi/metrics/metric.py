import dspy
from abc import abstractmethod

class Metric():
    def __init__(
            lm: Optional[dspy.LM] = None,
        ):
        self.lm = lm
       
    @abstractmethod 
    def eval(example, prediction, trace=None):
        raise NotImplementedError(
            f"Metric {type(self).__name__} is missing the required 'eval' method."
        )