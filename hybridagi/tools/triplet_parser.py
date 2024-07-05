import dspy
import re
import ast
from typing import Optional, List, Tuple
from .base import BaseTool
from ..output_parsers.prediction import PredictionOutputParser

class ExtractTripletsSignature(dspy.Signature):
    """Extract knowledge triplets from the given text."""
    objective = dspy.InputField(desc="The long-term objective (what you are doing)")
    context = dspy.InputField(desc="The previous actions (what you have done)")
    purpose = dspy.InputField(desc="The purpose of the action (what you have to do now)")
    prompt = dspy.InputField(desc="The action specific instructions (How to do it)")
    triplets = dspy.OutputField(desc="A list of knowledge triplets in the format (subject, predicate, object)")

class TripletParserTool(BaseTool):
    def __init__(
        self,
        lm: Optional[dspy.LM] = None,
    ):
        super().__init__(name="TripletParser", lm=lm)
        self.predict = dspy.Predict(ExtractTripletsSignature)
        self.prediction_parser = PredictionOutputParser()

    @staticmethod
    def parse_triplet(triplet_str: str) -> Optional[Tuple[str, str, str]]:
        """Parse a single triplet string into a tuple."""
        # Remove leading/trailing whitespace and newlines
        triplet_str = triplet_str.strip()
        
        # Try parsing with labels
        match = re.match(r'\(Subject:\s*(.+?),\s*Predicate:\s*(.+?),\s*Object:\s*(.+?)\)\s*$', triplet_str, re.DOTALL)
        if match:
            return tuple(item.strip() for item in match.groups())
        
        # Try parsing without labels
        match = re.match(r'\(([^,]+?),\s*([^,]+?),\s*([^,]+?)\)\s*$', triplet_str, re.DOTALL)
        if match:
            return tuple(item.strip().strip('"') for item in match.groups())
        
        # Try parsing list-like format
        match = re.match(r'\[([^,]+?),\s*([^,]+?)(?:,\s*([^,]+?))?\]', triplet_str, re.DOTALL)
        if match:
            return tuple(item.strip().strip('"') for item in match.groups() if item)
        
        return None

    @staticmethod
    def parse_triplets(triplets_str: str) -> List[Tuple[str, str, str]]:
        """Parse triplets string into a list of tuples."""
        triplets = []
        
        # Clean the input string
        triplets_str = triplets_str.strip()
        
        try:
            # Try to evaluate as a Python expression (for list format)
            eval_triplets = ast.literal_eval(triplets_str)
            if isinstance(eval_triplets, list):
                for item in eval_triplets:
                    if isinstance(item, (list, tuple)):
                        triplets.append(tuple(str(i).strip() for i in item) + ('',) * (3 - len(item)))
                    elif isinstance(item, str):
                        triplet = TripletParserTool.parse_triplet(item)
                        if triplet:
                            triplets.append(triplet)
                return triplets
            elif isinstance(eval_triplets, tuple):
                return [eval_triplets + ('',) * (3 - len(eval_triplets))]
        except (SyntaxError, ValueError):
            # If ast.literal_eval fails, continue with other parsing methods
            pass

        # Try to split the string into multiple triplets
        triplet_strings = re.findall(r'\((?:[^()]*|\([^()]*\))*\)|\[(?:[^[\]]*|\[[^[\]]*\])*\]', triplets_str)
        
        if triplet_strings:
            for triplet_str in triplet_strings:
                triplet = TripletParserTool.parse_triplet(triplet_str)
                if triplet:
                    triplets.append(triplet + ('',) * (3 - len(triplet)))
            return triplets

        # If all else fails, try to parse the entire string as a single triplet
        triplet = TripletParserTool.parse_triplet(triplets_str)
        if triplet:
            triplets = [triplet + ('',) * (3 - len(triplet))]
        
        return triplets

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

            triplets_str = self.prediction_parser.parse(pred.triplets, prefix="", stop=["\n\n"])
        else:
            triplets_str = prompt

        message = self.parse_triplets(triplets_str)

        return dspy.Prediction(
            message=message
        )

    def __deepcopy__(self, memo):
        return type(self)(
            lm=self.lm,
        )