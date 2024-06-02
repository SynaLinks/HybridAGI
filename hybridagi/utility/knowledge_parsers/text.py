import spacy
from .base import KnowledgeParserBase
from ...hybridstores.fact_memory.fact_memory import FactMemory

NLP = spacy.load("en_core_web_sm")

class TextKnowledgeParser(KnowledgeParserBase):
    
    def __init__(
            self,
            fact_memory: FactMemory,
            mode: str = "simple"
        ):
        super().__init__(fact_memory=fact_memory)
        self.mode = mode

    def parse(self, filename: str, content: str, mode: str = None):
        if mode is None:
            mode = self.mode
        triplets = self.extract_triplets(content, mode)
        
        for triplet in triplets:
            if len(triplet) != 3:   # Not a valid triplet
                continue
            metadata = {"filename": filename}
            for index, node in enumerate(triplet):
                if index != 1:  # Skip the second element of the triplet
                    self.fact_memory.add_texts(
                        texts=[node],
                        ids=[node],
                        metadatas=[metadata],
                    )
            self.fact_memory.add_triplet(triplet[0], triplet[1], triplet[2])

    def extract_triplets(self, text, mode: str) -> list:
        doc = NLP(text)
        
        triplets = []
        
        # Extract noun chunks for subjects and objects
        noun_chunks = list(doc.noun_chunks)
        
        for sent in doc.sents:
            if mode == "simple":
                subj = None
                verb = None
                obj = None

                for token in sent:
                    if "subj" in token.dep_:
                        subj = token
                    if token.pos_ == "VERB":
                        verb = token
                    if "obj" in token.dep_ or token.dep_ == "attr":
                        obj = token
                
                # Map tokens to noun chunks if possible
                def get_noun_chunk(token):
                    for chunk in noun_chunks:
                        if token in chunk:
                            return chunk.text
                    return token.text
                
                if subj and verb and obj:
                    triplets.append((get_noun_chunk(subj), verb.lemma_, get_noun_chunk(obj)))

            elif mode == "deep":
                subjects = []
                verbs = []
                objects = []
                indirect_objects = []

                for token in sent:
                    if "subj" in token.dep_:
                        subjects.append(token)
                    if token.pos_ == "VERB":
                        verbs.append(token)
                    if "obj" in token.dep_ or token.dep_ == "attr":
                        objects.append(token)
                    if token.dep_ == "iobj":
                        indirect_objects.append(token)
                
                # Map tokens to noun chunks if possible
                def get_noun_chunk(token):
                    for chunk in noun_chunks:
                        if token in chunk:
                            return chunk.text
                    return token.text
                
                for verb in verbs:
                    for subj in subjects:
                        for obj in objects:
                            triplets.append((get_noun_chunk(subj), verb.lemma_, get_noun_chunk(obj)))
                        for iobj in indirect_objects:
                            triplets.append((get_noun_chunk(subj), verb.lemma_, get_noun_chunk(iobj)))
        
        return triplets
