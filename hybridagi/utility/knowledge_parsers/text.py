# Text Knowledge Parser implementation based on article: https://medium.com/@erkajalkumari/knowledge-graphs-the-game-changer-in-ai-and-data-science-d56580b15aaa

import spacy
from spacy.matcher import Matcher
from .base import KnowledgeParserBase
from ...hybridstores.fact_memory.fact_memory import FactMemory

NLP = spacy.load("en_core_web_sm")

class TextKnowledgeParser(KnowledgeParserBase):
    
    def __init__(self, fact_memory: FactMemory):
        super().__init__(fact_memory=fact_memory)

    def parse(self, filename: str, content: str):
        triplets = self.extract_triplets(content)
        
        for triplet in triplets:
            if len(triplet) != 3:   # Not a valid triplet
                continue
            metadata = {"filename": filename}
            for index, node in enumerate(triplet):
                if index != 1:  # Skip the second element of the triplet
                    self.fact_memory.add_texts(
                        texts=[node],
                        ids=[node],
                        descriptions=[node],
                        metadatas=[metadata],
                    )
            self.fact_memory.add_triplet(triplet[0], triplet[1], triplet[2])

    def extract_triplets(self, text) -> list:
        doc = NLP(text)
        triplets = []

        for sent in doc.sents:
            entities = self.get_entities(sent.text)
            relation = self.get_relation(sent.text)

            if entities[0] and relation and entities[1]:
                triplets.append((entities[0], relation, entities[1]))

        return triplets

    def get_entities(self, sent):
        ent1 = ""
        ent2 = ""
        prv_tok_dep = ""
        prv_tok_text = ""
        prefix = ""
        modifier = ""

        for tok in NLP(sent):
            if tok.dep_ != "punct":
                if tok.dep_ == "compound":
                    prefix = tok.text
                    if prv_tok_dep == "compound":
                        prefix = prv_tok_text + " " + tok.text

                if tok.dep_.endswith("mod"):
                    modifier = tok.text
                    if prv_tok_dep == "compound":
                        modifier = prv_tok_text + " " + tok.text

                if tok.dep_.find("subj") != -1:
                    ent1 = modifier + " " + prefix + " " + tok.text
                    prefix = ""
                    modifier = ""
                    prv_tok_dep = ""
                    prv_tok_text = ""

                if tok.dep_.find("obj") != -1:
                    ent2 = modifier + " " + prefix + " " + tok.text

                prv_tok_dep = tok.dep_
                prv_tok_text = tok.text
        return [ent1.strip(), ent2.strip()]

    def get_relation(self, sent):
        doc = NLP(sent)
        matcher = Matcher(NLP.vocab)
        pattern = [{'DEP': 'ROOT'}, {'DEP': 'prep', 'OP': "?"}, {'DEP': 'agent', 'OP': "?"}, {'POS': 'ADJ', 'OP': "?"}]
        matcher.add("matching_1", [pattern])
        matches = matcher(doc)
        if matches:
            k = len(matches) - 1
            span = doc[matches[k][1]:matches[k][2]] 
            return span.text
        return ""
