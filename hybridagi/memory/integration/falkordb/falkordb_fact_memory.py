from typing import Union, List, Optional, Dict
import json
from uuid import UUID
from collections import OrderedDict
from hybridagi.memory.fact_memory import FactMemory
from hybridagi.core.datatypes import Entity, EntityList, Fact, FactList, Relationship, GraphProgram
from hybridagi.embeddings.embeddings import Embeddings
from .falkordb_memory import FalkorDBMemory

class FalkorDBFactMemory(FalkorDBMemory, FactMemory):
    """
    A class used to manage and store facts using FalkorDB.

    This class extends FalkorDBMemory and implements the FactMemory interface,
    providing a robust solution for storing and managing facts in a graph database.
    It allows for efficient storage, retrieval, and manipulation of entities and
    their relationships (facts) using FalkorDB's graph capabilities.
    """
   
    def __init__(
        self,
        index_name: str,
        graph_index: str = "fact_memory",
        hostname: str = "localhost",
        port: int = 6379,
        username: str = "",
        password: str = "",
        wipe_on_start: bool = False,
    ):
        super().__init__(
            index_name = index_name,
            graph_index = graph_index,
            hostname = hostname,
            port = port,
            username = username,
            password = password,
            wipe_on_start = wipe_on_start,
        )

    def exist(self, entity_or_fact_id: Union[UUID, str]) -> bool:
        """
        Check if a fact or entity exists in the database.

        Args:
            entity_or_fact_id: The ID of the fact or entity to check.

        Returns:
            bool: True if the fact or entity exists, False otherwise.
        """
        result = super().exist(entity_or_fact_id, "Entity")
        if result:
            return result
        else:
            return self.exist_fact(entity_or_fact_id)
        
    def exist_fact(self, index: Union[UUID, str]) -> bool:
        query = "MATCH ()-[r:FACT {_id_: $index}]->() RETURN r._id_ as id"
        result = self._graph.query(query, params={"index": str(index)})
        return len(result.result_set) > 0

    def update(self, entities_or_facts: Union[Entity, EntityList, Fact, FactList]) -> None:
        """
        Update the FalkorDB fact memory with new entities or facts.

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
                params = {
                    "id": ent_id,
                    "label": ent.label,
                    "name": ent.name,
                    "description": ent.description,
                    "vector": list(ent.vector) if ent.vector is not None else None,
                    "metadata": json.dumps(ent.metadata),
                }
                self._graph.query(
                    " ".join([
                    "MERGE (e:"+ent.label+":Entity {id: $id})",
                    "SET",
                    "e.name=$name,",
                    "e.label=$label,",
                    "e.description=$description,",
                    "e.metadata=$metadata,",
                    "e.vector=vecf32($vector)"]),
                    params = params,
                )
        else:
            if isinstance(entities_or_facts, Fact):
                facts = FactList()
                facts.facts = [entities_or_facts]
            else:
                facts = entities_or_facts
            for fact in facts.facts:
                fact_id = str(fact.id)
                if not self.exist(fact.subj.id):
                    self.update(fact.subj)
                if not self.exist(fact.obj.id):
                    self.update(fact.obj)
                params = {
                    "id": fact_id,
                    "subject_id": str(fact.subj.id),
                    "object_id": str(fact.obj.id),
                    "relationship": fact.rel.name,
                    "vector": list(fact.vector) if fact.vector is not None else None,
                    "metadata": json.dumps(fact.metadata),
                }
                self._graph.query(
                    " ".join([
                        "MATCH (s:Entity {id: $subject_id}),",
                        "(o:Entity {id: $object_id})",
                        "MERGE (s)-[r:FACT {_id_: $id}]->(o)",
                        "SET",
                        "r.relationship=$relationship,",
                        "r.vector=vecf32($vector),",
                        "r.metadata=$metadata",
                    ]),
                    params=params,
                )

    def remove(self, id_or_ids: Union[UUID, str, List[Union[UUID, str]]]) -> None:
        """
        Remove entities or facts from the FalkorDB fact memory.

        Parameters:
            id_or_ids (Union[UUID, str, List[Union[UUID, str]]]): A single entity or fact id or a list of entity or fact ids to be removed from the memory.
        """
        if not isinstance(id_or_ids, list):
            entities_ids = [id_or_ids]
        else:
            entities_ids = id_or_ids
        result = EntityList()
        ids = [str(i) for i in id_or_ids]
        self._graph.query(
            " ".join([
                "MATCH (e:Entity) WHERE e.id IN $ids",
                "DETACH DELETE e"]),
            params={"ids": ids}
        )
        self._graph.query(
            " ".join([
                "MATCH ()-[r:FACT {id: $id}]->()",
                "WHERE r.id IN $ids",
                "DELETE r"]),
            params={"ids": ids}
        )

    def get_entities(self, id_or_ids: Union[UUID, str, List[Union[UUID, str]]]) -> EntityList:
        """
        Retrieve entities from the FalkorDB fact memory.

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
        ids = [str(i) for i in id_or_ids]
        for entity_id in entities_ids:
            if self.exist(entity_id):
                query_result = self._graph.query(
                    " ".join(
                        [
                            "MATCH (e:Entity {id: $id})",
                            "RETURN",
                            "e.name as name,",
                            "e.label as label,",
                            "e.description as description,",
                            "e.vector as vector",
                        ]
                    ),
                    params={"id": entity_id}
                )
                try:
                    entity_id = UUID(entity_id)
                except Exception:
                    pass
                name = query_result.result_set[0][0]
                label = query_result.result_set[0][1]
                description = query_result.result_set[0][2]
                vector = query_result.result_set[0][3]
                entity = Entity(
                    id=entity_id,
                    name=name,
                    label=label,
                    description=description,
                    vector=vector,
                )
                result.entities.append(entity)
        return result

    def get_facts(self, id_or_ids: Union[UUID, str, List[Union[UUID, str]]]) -> FactList:
        """
        Retrieve facts from the FalkorDB fact memory.

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
            if self.exist_fact(fact_id):
                query_result = self._graph.query(
                    " ".join(
                        [
                            "MATCH (s:Entity)-[r:FACT {_id_:$id}]->(o:Entity)",
                            "RETURN",
                            "r.relationship as relationship_name,",
                            "r.metadata as metadata,",
                            "r.vector as relation_vector,",
                            "s.id as subject_id,",
                            "o.id as object_id",
                        ]
                    ),
                    params={"id": fact_id},
                )
                relationship_name = query_result.result_set[0][0]
                relationship_metadata = query_result.result_set[0][1]
                relationship_vector = query_result.result_set[0][2]
                subject_id = query_result.result_set[0][3]
                object_id = query_result.result_set[0][4]
                entities = self.get_entities([subject_id, object_id])
                subject_entity = entities.entities[0]
                object_entity = entities.entities[1]
                rel = Relationship(name=relationship_name)
                try:
                    fact_id = UUID(fact_id)
                except Exception:
                    pass
                fact = Fact(
                    id=fact_id,
                    subj=subject_entity,
                    rel=rel,
                    obj=object_entity,
                    vector=relationship_vector,
                    metadata=json.loads(relationship_metadata),
                )
                result.facts.append(fact)
        return result