import dspy
from tqdm import tqdm
from typing import Union
from hybridagi.embeddings.embeddings import Embeddings
from hybridagi.core.datatypes import Fact, FactList

class FactEmbedder(dspy.Module):
    """
    A class used to embed facts using a pre-trained embedding model.

    Attributes:
        embeddings (Embeddings): The pre-trained embedding model to be used for embedding facts.
    """    
    def __init__(
            self,
            embeddings: Embeddings
        ):
        """
        Initialize the FactEmbedder.

        Parameters:
            embeddings (Embeddings): The pre-trained embedding model to be used for embedding facts.
        """
        self.embeddings = embeddings 
    
    def forward(self, fact_or_facts: Union[Fact, FactList]) -> FactList:
        """
        Embed facts using the pre-trained embedding model.

        Parameters:
            fact_or_facts (Union[Fact, FactList]): A single fact or a list of facts to be embedded.

        Returns:
            FactList: A list of facts with their corresponding embeddings.

        Raises:
            ValueError: If the input is not a Fact or FactList.
        """
        if not isinstance(fact_or_facts, Fact) and not isinstance(fact_or_facts, FactList):
            raise ValueError(f"{type(self).__name__} input must be a Fact or FactList")
        if isinstance(fact_or_facts, Fact):
            facts = FactList()
            facts.facts = [fact_or_facts]
        else:
            facts = fact_or_facts
        for fact in tqdm(facts.facts):
            fact.vector = self.embeddings.embed_text(fact.subj.name+" "+fact.rel.name+" "+fact.obj.name)
        return facts