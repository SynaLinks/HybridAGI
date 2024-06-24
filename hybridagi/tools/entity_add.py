import dspy
import re
from typing import Optional, List
from .base import BaseTool
from ..output_parsers.prediction import PredictionOutputParser
from ..hybridstores.fact_memory.fact_memory import FactMemory
from ..embeddings.base import BaseEmbeddings

class ExtractTripletsSignature(dspy.Signature):
    """Extract knowledge triplets from the given text."""
    text = dspy.InputField(desc="The text to extract triplets from")
    triplets = dspy.OutputField(desc="""A list of knowledge triplets in the format (subject, predicate, object), DO NOT add any other content
    
    Example:
    London is the capital of England. Westminster is located in London.

    [
        ("Capital_of_England", "is", "London"),
        ("Location_of_Westminster", "within", "London"),
        ("Part_of_London", "is", "Westminster")
    ]
    """)

class EntityAddSignature(dspy.Signature):
    """Infer the correct document content and title based on given information."""
    objective = dspy.InputField(desc="The long-term objective (what you are doing)")
    context = dspy.InputField(desc="The previous actions (what you have done)")
    purpose = dspy.InputField(desc="The purpose of the action (what you have to do now)")
    prompt = dspy.InputField(desc="The action specific instructions (How to do it)")
    content = dspy.OutputField(desc="The content to convert to triplets")

class EntityAddTool(BaseTool):
    def __init__(
        self,
        fact_memory: FactMemory,
        embeddings: BaseEmbeddings,
        lm: Optional[dspy.LM] = None,
    ):
        super().__init__(name="EntityAdd", lm=lm)
        self.predict = dspy.Predict(EntityAddSignature)
        self.extract_triplets = dspy.Predict(ExtractTripletsSignature)
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
            
            triplets_pred = self.extract_triplets(text=pred.content)
            triplets_str = self.prediction_parser.parse(triplets_pred.triplets, prefix="", stop=["\n\n"])
            triplets_str = self.clean_triplets_string(triplets_str)
            
            try:
                pred.content = eval(triplets_str)
                message = self.add_triplets_to_fact_memory(pred.content)
            except Exception:
                pred.content = triplets_str
                message = "Error: Unable to parse triplets from LLM output. Document not processed."
        else:
            try:
                triplets = eval(prompt)
                message = self.add_triplets_to_fact_memory(triplets)
                pred = dspy.Prediction(content=triplets)
            except Exception:
                pred = dspy.Prediction(content=prompt)
                message = "Error: Unable to parse triplets from LLM output. Document not processed."

        return dspy.Prediction(
            content=pred.content,
            message=message
        )

    def __deepcopy__(self, memo):
        return type(self)(
            fact_memory=self.fact_memory,
            embeddings=self.embeddings,
            lm=self.lm,
        )