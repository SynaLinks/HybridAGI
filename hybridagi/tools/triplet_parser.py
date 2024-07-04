import dspy
import re
from typing import Optional
from .base import BaseTool
from ..output_parsers.prediction import PredictionOutputParser

class ExtractTripletsSignature(dspy.Signature):
    """Extract knowledge triplets from the given text."""
    objective = dspy.InputField(desc="The long-term objective (what you are doing)")
    context = dspy.InputField(desc="The previous actions (what you have done)")
    purpose = dspy.InputField(desc="The purpose of the action (what you have to do now)")
    prompt = dspy.InputField(desc="The action specific instructions (How to do it)")
    triplets = dspy.OutputField(desc="A list of knowledge triplets in the format (subject, predicate, object)")
    # triplets = dspy.OutputField(desc="""A list of knowledge triplets in the format (subject, predicate, object), DO NOT add any other content
    
    # Example:
    # London is the capital of England. Westminster is located in London.

    # [
    #     ("Capital_of_England", "is", "London"),
    #     ("Location_of_Westminster", "within", "London"),
    #     ("Part_of_London", "is", "Westminster")
    # ]
    # """)

class TripletParserTool(BaseTool):
    def __init__(
        self,
        lm: Optional[dspy.LM] = None,
    ):
        super().__init__(name="TripletParser", lm=lm)
        self.predict = dspy.Predict(ExtractTripletsSignature)
        self.prediction_parser = PredictionOutputParser()

    @staticmethod
    def clean_triplets_string(triplets_str: str) -> str:
        """Clean the triplets string."""
        start = triplets_str.find('[')
        end = triplets_str.rfind(']')
        
        if start != -1 and end != -1 and start < end:
            triplets_content = triplets_str[start:end+1]
            return re.sub(r'\s+', ' ', triplets_content).strip()
        return triplets_str.strip()

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

            triplets_str = self.prediction_parser.parse(pred.triplets, prefix="", stop=["\n"])
            triplets_str = self.clean_triplets_string(triplets_str)
            
            try:
                message = eval(triplets_str)
            except Exception:
                message = "Error: Unable to parse triplets from LLM output"
        else:
            try:
                message = eval(prompt)
            except Exception:
                message = "Error: Unable to parse triplets from LLM output."

        return dspy.Prediction(
            message=message
        )

    def __deepcopy__(self, memo):
        return type(self)(
            lm=self.lm,
        )