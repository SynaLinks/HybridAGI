import dspy
from tqdm import tqdm
from typing import Union
from hybridagi.embeddings.embeddings import Embeddings
from hybridagi.core.datatypes import Fact, FactList
from hybridagi.core.datatypes import Entity, EntityList

class EntityEmbedder(dspy.Module):
    """
    A class for embedding entities or facts using a pre-trained embedding model.

    Attributes:
        embeddings (Embeddings): The pre-trained embedding model to use.
    """
    def __init__(
            self,
            embeddings: Embeddings
        ):
        """
        Initializes the EntityEmbedder with an embedding model.

        Args:
            embeddings (Embeddings): The embedding model to use for embedding entities.
        """
        self.embeddings = embeddings
    
    def forward(self, facts_or_entities: Union[Entity, EntityList, Fact, FactList]) -> Union[EntityList, FactList]:
        """
        Embeds the given entities or facts using the embedding model.

        Args:
            facts_or_entities (Union[Entity, EntityList, Fact, FactList]): The entities or facts to embed.

        Returns:
            Union[EntityList, FactList]: The embedded entities or facts.

        Raises:
            ValueError: If the input is not a Fact or Entity or EntityList or FactList.
        """        
        if not isinstance(facts_or_entities, Fact) and \
            not isinstance(facts_or_entities, FactList) and \
                not isinstance(facts_or_entities, Entity) and \
                    not isinstance(facts_or_entities, EntityList):
            raise ValueError(f"{type(self).__name__} input must be a Fact or Entity or EntityList or FactList")
        if isinstance(facts_or_entities, Fact) or isinstance(facts_or_entities, FactList):
            if isinstance(facts_or_entities, Fact):
                facts = FactList()
                facts.facts = [facts_or_entities]
            else:
                facts = facts_or_entities
            for fact in tqdm(facts.facts):
                if fact.subj.description:
                    fact.subj.vector = self.embeddings.embed_text(fact.subj.description)
                else:
                    fact.subj.vector = self.embeddings.embed_text(fact.subj.name)
                if fact.obj.description:
                    fact.obj.vector = self.embeddings.embed_text(fact.obj.description)
                else:
                    fact.obj.vector = self.embeddings.embed_text(fact.obj.name)
            return facts
        else:
            if isinstance(facts_or_entities, Entity):
                entities = EntityList
                entities.entities = [facts_or_entities]
            else:
                entities = facts_or_entities
            for ent in tqdm(entities.entities):
                if ent.description:
                    ent.vector = self.embeddings.embed_text(ent.description)
                else:
                    ent.vector = self.embeddings.embed_text(ent.name)
            return entities