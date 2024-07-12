import dspy
from typing import Optional, List, Tuple
from .base import BaseTool
from ..output_parsers.prediction import PredictionOutputParser

class ParseTripletsSignature(dspy.Signature):
    """Parse knowledge triplets from the given text."""
    objective = dspy.InputField(desc="The long-term objective (what you are doing)")
    context = dspy.InputField(desc="The previous actions (what you have done)")
    purpose = dspy.InputField(desc="The purpose of the action (what you have to do now)")
    prompt = dspy.InputField(desc="The action specific instructions (How to do it)")
    triplets = dspy.OutputField(desc="""
    Knowledge graph triplets in one of the following formats:
    1. A list of tuples: [("subject1", "predicate1", "object1"), ("subject2", "predicate2", "object2")]
    2. A single tuple: ("subject", "predicate", "object")
    Ensure to use double quotes for strings and parentheses for tuples.
    """)

class TripletParserTool(BaseTool):
    def __init__(
        self,
        lm: Optional[dspy.LM] = None,
    ):
        super().__init__(name="TripletParser", lm=lm)
        self.predict = dspy.Predict(ParseTripletsSignature)
        self.prediction_parser = PredictionOutputParser()

    def forward(
        self,
        context: str,
        objective: str,
        purpose: str,
        prompt: str,
        disable_inference: bool = False,
    ) -> dspy.Prediction:
        """Perform DSPy forward prediction."""
        if not disable_inference:
            with dspy.context(lm=self.lm or dspy.settings.lm):
                pred = self.predict(
                    objective=objective,
                    context=context,
                    purpose=purpose,
                    prompt=prompt,
                )
            message = self.prediction_parser.parse(pred.triplets, prefix="", stop=["\n\n"])
        else:
            message = prompt
        return dspy.Prediction(
            message = message
        )

    def __deepcopy__(self, memo):
        return type(self)(
            lm=self.lm,
        )