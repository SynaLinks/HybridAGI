import dspy
import re
from typing import Optional, List, Union
from .base import BaseTool
from ..output_parsers.prediction import PredictionOutputParser
from ..hybridstores.fact_memory.fact_memory import FactMemory
from ..embeddings.base import BaseEmbeddings
from ..tools.triplet_parser import ExtractTripletsSignature

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

    def parse_triplets(self, triplets_input: Union[str, List]) -> List[tuple]:
        """Parse triplets from either a string or a list."""
        if isinstance(triplets_input, str):
            triplets_str = self.clean_triplets_string(triplets_input)
            try:
                return eval(triplets_str)
            except Exception:
                raise ValueError("Unable to parse triplets from string input.")
        elif isinstance(triplets_input, list):
            return triplets_input
        else:
            raise ValueError("Invalid triplets input type. Expected string or list.")

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
                triplets_str = self.prediction_parser.parse(pred.triplets , prefix="", stop=["\n"])
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