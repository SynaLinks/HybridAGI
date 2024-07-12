import ast
import dspy
import re
import json
from typing import Optional, List, Tuple
from .base import BaseTool
from ..output_parsers.prediction import PredictionOutputParser
from ..hybridstores.fact_memory.fact_memory import FactMemory
from ..embeddings.base import BaseEmbeddings

class EntityAddToolSignature(dspy.Signature):
    """You will be given knowledge graph triplets in the format [(subject, predicate, object)]"""
    objective = dspy.InputField(desc="The long-term objective (what you are doing)")
    context = dspy.InputField(desc="The previous actions (what you have done)")
    purpose = dspy.InputField(desc="The purpose of the action (what you have to do now)")
    prompt = dspy.InputField(desc="The action specific instructions (How to do it)")
    triplets = dspy.OutputField(desc="Knowledge graph triplets in the format [(subject, predicate, object)]")

class EntityAddTool(BaseTool):
    def __init__(
        self,
        fact_memory: FactMemory,
        embeddings: BaseEmbeddings,
        lm: Optional[dspy.LM] = None,
    ):
        super().__init__(name="EntityAdd", lm=lm)
        self.predict = dspy.Predict(EntityAddToolSignature)
        self.prediction_parser = PredictionOutputParser()
        self.fact_memory = fact_memory
        self.embeddings = embeddings

    def parse_triplets(self, input_str: str) -> List[Tuple[str, str, str]]:
        """
        Parse various triplet representations and return a list of (subject, predicate, object) tuples.
        
        :param input_str: A string containing triplet information in various formats
        :return: A list of (subject, predicate, object) tuples
        """
        def clean_triplet(triplet: Tuple[str, str, str]) -> Tuple[str, str, str]:
            return tuple(item.strip() for item in triplet)

        triplets_section = re.search(r'Triplets:\s*([\s\S]*)', input_str, re.IGNORECASE)
        triplets_section = triplets_section.group(1) if triplets_section else input_str

        # Try to parse as a markdown table
        table_pattern = r'\s*\|?\s*([^|\n]+?)\s*\|\s*([^|\n]+?)\s*\|\s*([^|\n]+?)\s*\|?\s*\n'
        table_matches = re.findall(table_pattern, triplets_section)
        if table_matches:
            data_rows = [row for row in table_matches[2:] if not any('---' in cell for cell in row)]
            if data_rows:
                return [clean_triplet(row) for row in data_rows]

        # Try to parse as a list of lists or tuples
        try:
            parsed_data = ast.literal_eval(triplets_section.strip())
            if isinstance(parsed_data, list) and all(isinstance(item, (list, tuple)) and len(item) == 3 for item in parsed_data):
                return [clean_triplet(item) for item in parsed_data]
        except (ValueError, SyntaxError):
            pass

        # Try to parse as JSON
        try:
            json_data = json.loads(triplets_section)
            if isinstance(json_data, list):
                return [clean_triplet((item['subject'], item['predicate'], item['object'])) 
                        for item in json_data 
                        if isinstance(item, dict) and all(key in item for key in ['subject', 'predicate', 'object'])]
        except json.JSONDecodeError:
            pass

        # Parse various string formats
        patterns = [
            r'\(Subject:\s*(.+?),\s*Predicate:\s*(.+?),\s*Object:\s*(.+?)\)',
            r'\d+\.\s*\("([^"]+)",\s*"([^"]+)",\s*"([^"]+)"\)',
            r'\(([^,]+),\s*([^,]+),\s*(.+?)\)',
            r'\("(.+?)",\s*"(.+?)",\s*"(.+?)"\)',
        ]

        for pattern in patterns:
            matches = re.findall(pattern, triplets_section, re.DOTALL)
            if matches:
                return [clean_triplet(match) for match in matches]

        # Parse Entity-Role-Facts format
        entity_pattern = r'Entity:\s*(.+?)\s*-\s*Role:\s*(.+?)\s*-\s*Facts:'
        fact_pattern = r'Facts:\s*(.+?)(?:\s*-\s*Facts:|$)'
        
        triplets = []
        for entity_match in re.finditer(entity_pattern, triplets_section, re.DOTALL):
            entity = entity_match.group(1).strip()
            role = entity_match.group(2).strip()
            
            facts_section = triplets_section[entity_match.end():triplets_section.find('Entity:', entity_match.end())]
            facts_section = facts_section if facts_section != -1 else triplets_section[entity_match.end():]
            
            for fact_match in re.finditer(fact_pattern, facts_section, re.DOTALL):
                fact = fact_match.group(1).strip()
                triplets.append((entity, 'has fact', fact) if role.lower() == 'subject' else (fact, 'is about', entity))
        
        return triplets if triplets else []

    def add_triplets_to_fact_memory(self, triplets: List[Tuple[str, str, str]]) -> str:
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
        try:
            if not disable_inference:
                with dspy.context(lm=self.lm or dspy.settings.lm):
                    pred = self.predict(
                        objective=objective,
                        context=context,
                        purpose=purpose,
                        prompt=prompt,
                    )
                triplets_str = self.prediction_parser.parse(pred.triplets, prefix="", stop=["\n\n\n"])
                triplets = self.parse_triplets(triplets_str)
            else:
                triplets = self.parse_triplets(objective)
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