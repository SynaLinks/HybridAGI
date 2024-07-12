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
        # Check if the input contains the structured format with Objective, Context, Purpose, Prompt
        structured_match = re.search(r'Triplets:\s*([\s\S]*)', input_str, re.IGNORECASE)
        if structured_match:
            triplets_section = structured_match.group(1)
        else:
            triplets_section = input_str

        # Try to parse as a markdown table
        table_pattern = r'\s*\|?\s*([^|\n]+?)\s*\|\s*([^|\n]+?)\s*\|\s*([^|\n]+?)\s*\|?\s*\n'
        table_matches = re.findall(table_pattern, triplets_section)
        if table_matches:
            # Exclude header and separator rows
            data_rows = table_matches[2:] if len(table_matches) > 2 else table_matches
            # Further filter out any remaining separator rows
            data_rows = [row for row in data_rows if not any('---' in cell for cell in row)]
            if len(data_rows) > 0:
                return [(s.strip(), p.strip(), o.strip()) for s, p, o in data_rows]

        # Try to parse as a list of lists
        try:
            cleaned_input = triplets_section.strip()
            list_of_lists = ast.literal_eval(cleaned_input)
            if isinstance(list_of_lists, list):
                triplets = [tuple(item) for item in list_of_lists if isinstance(item, list) and len(item) == 3]
                if triplets:
                    return [(s.strip(), p.strip(), o.strip()) for s, p, o in triplets]
        except (ValueError, SyntaxError):
            pass

        # Try to parse as JSON
        try:
            json_data = json.loads(triplets_section)
            if isinstance(json_data, list):
                triplets = [(item['subject'], item['predicate'], item['object']) 
                            for item in json_data 
                            if isinstance(item, dict) and all(key in item for key in ['subject', 'predicate', 'object'])]
                if triplets:
                    return [(s.strip(), p.strip(), o.strip()) for s, p, o in triplets]
        except json.JSONDecodeError:
            pass

        # Pattern for the format: (Subject: s, Predicate: p, Object: o.)
        pattern1 = r'\(Subject:\s*(.+?),\s*Predicate:\s*(.+?),\s*Object:\s*(.+?)\)'
        matches1 = re.findall(pattern1, triplets_section, re.DOTALL)
        if matches1:
            return [(s.strip(), p.strip(), o.strip()) for s, p, o in matches1]

        # Pattern for the numbered list format: 1. ("subject", "predicate", "object")
        numbered_list_pattern = r'\d+\.\s*\("([^"]+)",\s*"([^"]+)",\s*"([^"]+)"\)'
        numbered_list_matches = re.findall(numbered_list_pattern, triplets_section)
        if numbered_list_matches:
            return [(s.strip(), p.strip(), o.strip()) for s, p, o in numbered_list_matches]

        # Pattern for the format: [(subject, predicate, object), ...]
        tuple_pattern = r'\(([^,]+),\s*([^,]+),\s*(.+?)\)'
        tuple_matches = re.findall(tuple_pattern, triplets_section)
        if tuple_matches:
            return [(s.strip(), p.strip(), o.strip()) for s, p, o in tuple_matches]

        # Pattern for the format: ("subject", "predicate", "object")
        pattern2 = r'\("(.+?)",\s*"(.+?)",\s*"(.+?)"\)'
        matches2 = re.findall(pattern2, triplets_section)
        if matches2:
            return [(s.strip(), p.strip(), o.strip()) for s, p, o in matches2]

        # Pattern for the format provided: Entity: e - Role: r - Facts: f.
        entity_pattern = r'Entity:\s*(.+?)\s*-\s*Role:\s*(.+?)\s*-\s*Facts:'
        fact_pattern = r'Facts:\s*(.+?)(?:\s*-\s*Facts:|$)'
        
        entity_matches = re.finditer(entity_pattern, triplets_section, re.DOTALL)
        triplets = []
        for entity_match in entity_matches:
            entity = entity_match.group(1).strip()
            role = entity_match.group(2).strip()
            
            start = entity_match.end()
            end = triplets_section.find('Entity:', start)
            if end == -1:
                end = len(triplets_section)
            
            facts_section = triplets_section[start:end]
            fact_matches = re.finditer(fact_pattern, facts_section, re.DOTALL)
            
            for fact_match in fact_matches:
                fact = fact_match.group(1).strip()
                if role.lower() == 'subject':
                    triplets.append((entity, 'has fact', fact))
                else:
                    triplets.append((fact, 'is about', entity))
        
        if triplets:
            return triplets

        # New pattern for numbered simple format: n. subject, predicate, object
        numbered_simple_pattern = r'\d+\.\s*([^,]+),\s*([^,]+),\s*(.+)'
        numbered_simple_matches = re.findall(numbered_simple_pattern, triplets_section)
        if numbered_simple_matches:
            return [(s.strip(), p.strip(), o.strip()) for s, p, o in numbered_simple_matches]

        # New pattern for simple format: subject, predicate, object
        simple_pattern = r'([^,]+),\s*([^,]+),\s*(.+)'
        simple_matches = re.findall(simple_pattern, triplets_section)
        if simple_matches:
            return [(s.strip(), p.strip(), o.strip()) for s, p, o in simple_matches]

        # If no format matched, return an empty list
        return []

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
                print(objective)
                triplets = self.parse_triplets(objective)
                print(triplets)
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