import ast
import dspy
import re
from typing import Optional, List, Tuple
from .base import BaseTool
from ..output_parsers.prediction import PredictionOutputParser
from ..hybridstores.fact_memory.fact_memory import FactMemory
from ..embeddings.base import BaseEmbeddings
from ..tools.triplet_parser import ExtractTripletsSignature, TripletParserTool

class EntityAddTool(BaseTool):
    def __init__(
        self,
        fact_memory: FactMemory,
        embeddings: BaseEmbeddings,
        lm: Optional[dspy.LM] = None,
    ):
        super().__init__(name="EntityAdd", lm=lm)
        self.predict = dspy.Predict(ExtractTripletsSignature)
        self.prediction_parser = PredictionOutputParser()
        self.fact_memory = fact_memory
        self.embeddings = embeddings
    
    @staticmethod
    def clean_triplets_string(triplets_str: str) -> str:
        """Clean the triplets string."""
        start = triplets_str.find('[')
        end = triplets_str.rfind(']')
        
        if start != -1 and end != -1 and start < end:
            triplets_content = triplets_str[start:end+1]
            return re.sub(r'\s+', ' ', triplets_content).strip()
        return triplets_str.strip()

    def add_triplets_to_fact_memory(self, triplets: List[tuple]) -> str:
        """Add valid triplets to FactMemory."""
        valid_triplets = 0
        for subject, predicate, obj in triplets:
            print(subject, predicate, obj)
            if all((subject, predicate, obj)):
                for node in (subject, obj):
                    self.fact_memory.add_texts(
                        texts=[node],
                        ids=[node],
                        descriptions=[node],
                    )
                self.fact_memory.add_triplet(subject, predicate, obj)
                valid_triplets += 1
        
        return f"Processed document: {valid_triplets} valid triplets added to FactMemory."
    
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
        try:
            if not disable_inference:
                with dspy.context(lm=self.lm or dspy.settings.lm):
                    pred = self.predict(
                        objective=objective,
                        context=context,
                        purpose=purpose,
                        prompt=prompt,
                    )
                print(pred.triplets)
                # trace = "\n".join(self.agent_state.program_trace[-self.num_history:])
                triplets_str = self.prediction_parser.parse(pred.triplets , prefix="", stop=["\n\n"])
                triplets_str = self.clean_triplets_string(triplets_str)
                triplets = self.parse_triplets(pred.triplets)
            else:
                triplets = self.parse_triplets(prompt)

            results = self.add_triplets_to_fact_memory(triplets)
        except Exception as e:
            results = f"Error: {str(e)}"

        return dspy.Prediction(message=results)

    def __deepcopy__(self, memo):
        return type(self)(
            fact_memory=self.fact_memory,
            embeddings=self.embeddings,
            lm=self.lm,
        )