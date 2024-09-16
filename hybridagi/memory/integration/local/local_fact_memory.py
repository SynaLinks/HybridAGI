from collections import OrderedDict
from typing import Union, List, Dict, Optional
from uuid import UUID
from hybridagi.memory.fact_memory import FactMemory
from hybridagi.core.datatypes import Entity, EntityList
from hybridagi.core.datatypes import Fact, FactList
import networkx as nx
import random

from .local_memory import LocalMemory


def random_color():
    """Utilitary function to generate a random color"""
    return "#%06x" % random.randint(0, 0xFFFFFF)


class LocalFactMemory(LocalMemory, FactMemory):
    """
    A class used to manage and store facts locally.

    Attributes:
        index_name (str): The name of the index used for fact storage.
        wipe_on_start (bool): Whether to clear the memory when the object is initialized.
        _entities (Optional[Dict[str, Entity]]): A dictionary to store entities. The keys are entity IDs and the values are Entity objects.
        _relationships (Optional[Dict[str, Entity]]): A dictionary to store entities. The keys are relationships IDs and the values are Relationship objects.
        _facts (Optional[Dict[str, Fact]]): A dictionary to store facts. The keys are fact IDs and the values are Fact objects.
        _entities_embeddings (Optional[Dict[str, List[float]]]): An ordered dictionary to store entity embeddings. The keys are entity IDs and the values are lists of floats representing the embeddings.
        _relationships_embeddings (Optional[Dict[str, List[float]]]): An ordered dictionary to store relationships embeddings. The keys are relationships IDs and the values are lists of floats representing the embeddings.
        _facts_embeddings (Optional[Dict[str, List[float]]]): An ordered dictionary to store fact embeddings. The keys are fact IDs and the values are lists of floats representing the embeddings.
        _graph (nx.MultiDiGraph): A directed multigraph to store the relationships between entities.
        _labels_colors (Optional[Dict[str, str]]): A dictionary to store the colors associated with each label. The keys are labels and the values are colors.
    """
    index_name: str
    wipe_on_start: bool
    _entities: Optional[Dict[str, Entity]] = {}
    _relationships: Optional[Dict[str, Fact]] = {}
    _facts: Optional[Dict[str, Fact]] = {}
    
    _entities_embeddings: Optional[Dict[str, List[float]]] = OrderedDict()
    _relationships_embeddings: Optional[Dict[str, List[float]]] = OrderedDict()
    _facts_embeddings: Optional[Dict[str, List[float]]] = OrderedDict()
    
    _graph = nx.MultiDiGraph()
    
    _labels_colors: Optional[Dict[str, str]] = {}
    
    def __init__(
            self,
            index_name: str,
            wipe_on_start: bool=True,
        ):
        """
        Initialize the local fact memory.

        Parameters:
            index_name (str): The name of the index used for fact storage.
            wipe_on_start (bool): Whether to clear the memory when the object is initialized.
        """
        self.index_name = index_name
        if wipe_on_start:
            self.clear()
            
    def exist(self, fact_or_entity_id) -> bool:
        return fact_or_entity_id in self._entities or fact_or_entity_id in self._facts
            
    def update(self, entities_or_facts: Union[Entity, EntityList, Fact, FactList]) -> None:
        """
        Update the local fact memory with new entities or facts.

        Parameters:
            entities_or_facts (Union[Entity, EntityList, Fact, FactList]): An entity or a list of entities, or a fact or a list of facts to be added to the memory.

        Raises:
            ValueError: If the input is not an Entity, EntityList, Fact, or FactList.
        """
        if not isinstance(entities_or_facts, (Entity, EntityList, Fact, FactList)):
            raise ValueError("Invalid datatype provided must be Entity, EntityList, Fact or FactList")
        if isinstance(entities_or_facts, Entity) or isinstance(entities_or_facts, EntityList):
            if isinstance(entities_or_facts, Entity):
                entities = EntityList()
                entities.entities = [entities_or_facts]
            else:
                entities = entities_or_facts
            for ent in entities.entities:
                ent_id = str(ent.id)
                if ent_id not in self._entities:
                    if ent.label in self._labels_colors:
                        color = self._labels_colors[ent.label]
                    else:
                        color = random_color()
                        self._labels_colors[ent.label] = color
                    self._entities[ent_id] = ent
                    self._graph.add_node(ent_id, color=color, title=ent.label+"("+ent.description+")" if ent.description else ent.label+"("+ent.name+")")
                else:
                    self._entities[ent_id] = ent
                    self._graph.node(ent_id)["title"] = ent.label+"("+ent.description+")" if ent.description else ent.label+"("+ent.name+")"
                if ent.vector is not None:
                    self._entities_embeddings[ent_id] = ent.vector
        else:
            if isinstance(entities_or_facts, Fact):
                facts = FactList()
                facts.facts = [entities_or_facts]
            else:
                facts = entities_or_facts
            for fact in facts.facts:
                fact_id = str(fact.id)
                if fact_id not in self._facts:
                    subject_id = str(fact.subj.id)
                    object_id = str(fact.obj.id)
                    if subject_id not in self._entities:
                        self.update(fact.subj)
                    if object_id not in self._entities:
                        self.update(fact.obj)
                    self._facts[fact_id] = fact
                    self._graph.add_edge(subject_id, object_id, key=fact.rel.name, label=fact.rel.name)
                else:
                    subject_id = str(fact.subj.id)
                    object_id = str(fact.obj.id)
                    if subject_id not in self._entities:
                        self.update(fact.subj)
                    if object_id not in self._entities:
                        self.update(fact.obj)
                    previous_fact = self._facts[fact_id]
                    if self._graph.has_edge(previous_fact.subj.id, previous_fact.obj.id, key=previous_fact.rel.name):
                        self._graph.remove_edge(previous_fact.subj.id, previous_fact.obj.id, key=previous_fact.rel.name)
                    self._facts[fact_id] = fact
                    self._graph.add_edge(subject_id, object_id, key=fact.rel.name, label=fact.rel.name)
                if fact.vector is not None:
                    self._facts_embeddings[fact_id] = fact.vector
    
    def remove(self, id_or_ids: Union[UUID, str, List[Union[UUID, str]]]) -> None:
        """
        Remove entities or facts from the local fact memory.

        Parameters:
            id_or_ids (Union[UUID, str, List[Union[UUID, str]]]): A single entity or fact id or a list of entity or fact ids to be removed from the memory.
        """
        if not isinstance(id_or_ids, list):
            entities_or_facts_ids = [id_or_ids]
        else:
            entities_or_facts_ids = id_or_ids
        for fact_or_entity_id in entities_or_facts_ids:
            fact_or_entity_id = str(fact_or_entity_id)
            if fact_or_entity_id in self._facts:
                subject_id = str(self._facts[fact_or_entity_id].subj.id)
                object_id = str(self._facts[fact_or_entity_id].obj.id)
                label = self._facts[fact_or_entity_id].rel.name
                self._graph.remove_edge((subject_id, object_id), key=label)
                del self._facts[fact_or_entity_id]
                if fact_or_entity_id in self._facts_embeddings:
                    del self._facts_embeddings[fact_or_entity_id]
            elif fact_or_entity_id in self._entities:
                self._graph.remove_node([fact_or_entity_id])
                del self._entities[fact_or_entity_id]
                if fact_or_entity_id in self._entities_embeddings:
                    del self._entities_embeddings[fact_or_entity_id]

    def get_entities(self, id_or_ids: Union[UUID, str, List[Union[UUID, str]]]) -> EntityList:
        """
        Retrieve entities from the local fact memory.

        Parameters:
            id_or_ids (Union[UUID, str, List[Union[UUID, str]]]): A single entity id or a list of entity ids to be retrieved from the memory.

        Returns:
            EntityList: A list of entities that match the input ids.
        """
        if not isinstance(id_or_ids, list):
            entities_ids = [id_or_ids]
        else:
            entities_ids = id_or_ids
        result = EntityList()
        for entity_id in entities_ids:
            entity_id = str(entity_id)
            if entity_id in self._entities:
                entity = self._entities[entity_id]
                result.entities.append(entity)
        return result
    
    def get_facts(self, id_or_ids: Union[UUID, str, List[Union[UUID, str]]]) -> FactList:
        """
        Retrieve facts from the local fact memory.

        Parameters:
            id_or_ids (Union[UUID, str, List[Union[UUID, str]]]): A single fact id or a list of fact ids to be retrieved from the memory.

        Returns:
            FactList: A list of facts that match the input ids.
        """
        if not isinstance(id_or_ids, list):
            facts_ids = [id_or_ids]
        else:
            facts_ids = id_or_ids
        result = FactList()
        for fact_id in facts_ids:
            fact_id = str(fact_id)
            if fact_id in self._facts:
                fact = self._facts[fact_id]
                result.facts.append(fact)
        return result
        
    def clear(self):
        """
        Clear the local document memory.
        This method removes all entities, facts, graph, and embeddings from the memory.
        """
        self._entities = {}
        self._facts = {}
        self._graph = nx.MultiDiGraph()
        self._entities_embeddings = OrderedDict()
        self._facts_embeddings = OrderedDict()
        self._labels_colors = {}
