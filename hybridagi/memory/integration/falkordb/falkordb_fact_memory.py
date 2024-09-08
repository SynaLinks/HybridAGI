#TODO finish it

from typing import Union, List, Optional, Dict
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

    Key features:
    1. Entity management: Store and retrieve entities with their properties.
    2. Fact storage: Represent relationships between entities as facts.
    3. Efficient querying: Utilize FalkorDB's graph querying capabilities for fast data retrieval.
    4. Vector embeddings: Support for storing and querying vector embeddings of entities and facts.
    5. CRUD operations: Implement create, read, update, and delete operations for both entities and facts.

    This implementation provides a scalable and flexible solution for fact-based
    knowledge representation in AI and machine learning applications.
    """
   
    def __init__(
        self,
        index_name: str,
        embeddings: Embeddings,
        graph_index: str = "fact_memory",
        hostname: str = "localhost",
        port: int = 6379,
        username: str = "",
        password: str = "",
        indexed_label: str = "Entity",
        wipe_on_start: bool = False,
    ):
        super().__init__(
            index_name = index_name,
            graph_index = graph_index,
            embeddings = embeddings,
            hostname = hostname,
            port = port,
            username = username,
            password = password,
            indexed_label = indexed_label,
            wipe_on_start = wipe_on_start,
        )

    def exist(self, fact_or_entity_id) -> bool:
        """
        Check if a fact or entity exists in the database.

        Args:
            fact_or_entity_id: The ID of the fact or entity to check.

        Returns:
            bool: True if the fact or entity exists, False otherwise.
        """
        query = (
            "MATCH (e:Entity {id: $id}) RETURN COUNT(e) AS count "
            "UNION ALL "
            "MATCH ()-[r:RELATION {id: $id}]->() RETURN COUNT(r) AS count"
        )
        params = {"id": str(fact_or_entity_id)}
        result = self.hybridstore.query(query, params=params)
        return sum(int(count[0]) for count in result.result_set) > 0

    def _update_entities(self, entities: Union[Entity, EntityList]) -> None:
        """
        Update or create entities in the FalkorDB graph and local cache.

        This method takes either a single Entity or an EntityList and updates or creates
        the corresponding nodes in the graph and local cache. If an entity with the given ID already exists,
        its properties are updated. If it doesn't exist, a new entity node is created.

        Args:
            entities (Union[Entity, EntityList]): The entity or list of entities to update or create.

        Note:
            - The method uses a MERGE operation, which either matches existing nodes or creates new ones.
            - Entity properties (name, description, and vector) are updated or set.
            - The vector is converted to a list if present, or set to None if not available.
            - The label is included in the properties instead of being part of the node label.
            - The entity is also stored in the local cache (_entities) and its embedding in _entities_embeddings.
        """
        entities = [entities] if isinstance(entities, Entity) else entities.entities
        for entity in entities:
            params = {
                "id": str(entity.id),
                "properties": {
                    "name": entity.name,
                    "label": entity.label,
                    "description": entity.description,
                    "vector": list(entity.vector) if entity.vector is not None else None
                }
            }
            query = "MERGE (e:Entity {id: $id}) SET e += $properties"
            self.hybridstore.query(query, params=params)

            # Update local cache
            self._entities[str(entity.id)] = entity
            if entity.vector is not None:
                self._entities_embeddings[str(entity.id)] = list(entity.vector)

    def _update_facts(self, facts: Union[Fact, FactList]) -> None:
        """
        Update or create facts in the FalkorDB graph.

        This method takes either a single Fact or a FactList and updates or creates
        the corresponding relationships in the graph. It also ensures that the subject
        and object entities of each fact are updated or created.

        Args:
            facts (Union[Fact, FactList]): The fact or list of facts to update or create.

        Note:
            - The method first updates the subject and object entities of each fact.
            - It then uses a MERGE operation to either match existing relationships or create new ones.
            - Fact properties (name and vector) are updated or set on the relationship.
            - The vector is converted to a list if present, or set to None if not available.
        """
        facts = [facts] if isinstance(facts, Fact) else facts.facts
        for fact in facts:
            self._update_entities(fact.subj)
            self._update_entities(fact.obj)
            params = {
                "id": str(fact.id),
                "subject_id": str(fact.subj.id),
                "object_id": str(fact.obj.id),
                "properties": {
                    "name": fact.rel.name,
                    "vector": list(fact.vector) if fact.vector is not None else None
                }
            }
            self.hybridstore.query(
                "MATCH (s:Entity {id: $subject_id}), (o:Entity {id: $object_id}) "
                "MERGE (s)-[r:RELATION {id: $id}]->(o) "
                "SET r += $properties",
                params=params
            )

    def get_entities(self, id_or_ids: Union[UUID, str, List[Union[UUID, str]]]) -> EntityList:
        """
        Retrieve entities from the database.

        Args:
            id_or_ids: The ID(s) of the entities to retrieve. Can be a single UUID or string,
                       or a list of UUIDs or strings.

        Returns:
            EntityList: A list of retrieved entities.
        """
        ids = [str(id_or_ids)] if isinstance(id_or_ids, (UUID, str)) else [str(id) for id in id_or_ids]
        result = self.hybridstore.query(
            "MATCH (e:Entity) WHERE e.id IN $ids "
            "RETURN e",
            params={"ids": ids}
        )
        entities = EntityList()
        for row in result.result_set:
            entity_data = row[0]
            entity = Entity(
                id=entity_data.properties.get('id'),
                name=entity_data.properties.get('name'),
                label=entity_data.properties.get('label'),
                description=entity_data.properties.get('description'),
                vector=entity_data.properties.get('vector')
            )
            entities.entities.append(entity)
        return entities

    def get_facts(self, id_or_ids: Union[UUID, str, List[Union[UUID, str]]]) -> FactList:
        """
        Retrieve facts from the database.

        Args:
            id_or_ids: The ID(s) of the facts to retrieve. Can be a single UUID or string,
                       or a list of UUIDs or strings.

        Returns:
            FactList: A list of retrieved facts.
        """
        ids = [str(id_or_ids)] if isinstance(id_or_ids, (UUID, str)) else [str(id) for id in id_or_ids]
        result = self.hybridstore.query(
            "MATCH (s:Entity)-[r:RELATION]->(o:Entity) WHERE r.id IN $ids "
            "RETURN r, s, o",
            params={"ids": ids}
        )
        facts = FactList()
        for row in result.result_set:
            fact_data, subject_data, object_data = row
            subject = Entity(id=subject_data.properties.get('id'), name=subject_data.properties.get('name'), 
                             label=subject_data.properties.get('label'), description=subject_data.properties.get('description'), 
                             vector=subject_data.properties.get('vector'))
            relation = Relationship(name=fact_data.properties.get('name'))
            object = Entity(id=object_data.properties.get('id'), name=object_data.properties.get('name'), 
                            label=object_data.properties.get('label'), description=object_data.properties.get('description'), 
                            vector=object_data.properties.get('vector'))
            fact = Fact(id=fact_data.properties.get('id'), subj=subject, rel=relation, obj=object)
            facts.facts.append(fact)
        return facts

    def get_related_facts(self, entity_id: Union[UUID, str], relation: Optional[str] = None) -> FactList:
        """
        Retrieve facts related to a specific entity.

        Args:
            entity_id: The ID of the entity to find related facts for.
            relation: Optional relation type to filter the facts.

        Returns:
            FactList: A list of facts related to the given entity.
        """
        query = (
            "MATCH (e:Entity {id: $entity_id})-[r:RELATION]->(o:Entity) "
            "WHERE $relation IS NULL OR r.name = $relation "
            "RETURN r AS fact, e AS subject, o AS object "
            "UNION "
            "MATCH (s:Entity)-[r:RELATION]->(e:Entity {id: $entity_id}) "
            "WHERE $relation IS NULL OR r.name = $relation "
            "RETURN r AS fact, s AS subject, e AS object"
        )
        params = {"entity_id": str(entity_id), "relation": relation}
        result = self.hybridstore.query(query, params=params)
        
        facts = FactList()
        for row in result.result_set:
            fact_data, subject_data, object_data = row
            subject = Entity(id=subject_data.properties.get('id'), name=subject_data.properties.get('name'), 
                             label=subject_data.properties.get('label'), description=subject_data.properties.get('description'), 
                             vector=subject_data.properties.get('vector'))
            relation = Relationship(name=fact_data.properties.get('name'))
            object = Entity(id=object_data.properties.get('id'), name=object_data.properties.get('name'), 
                            label=object_data.properties.get('label'), description=object_data.properties.get('description'), 
                            vector=object_data.properties.get('vector'))
            fact = Fact(id=fact_data.properties.get('id'), subj=subject, rel=relation, obj=object)
            facts.facts.append(fact)
        return facts

    def get_entities_by_type(self, entity_type: str) -> EntityList:
        """
        Retrieve entities of a specific type.

        Args:
            entity_type: The type (label) of entities to retrieve.

        Returns:
            EntityList: A list of entities of the specified type.
        """
        query = "MATCH (e:Entity {label: $entity_type}) RETURN e"
        params = {"entity_type": entity_type}
        result = self.hybridstore.query(query, params=params)
        
        entities = EntityList()
        for row in result.result_set:
            entity_data = row[0]
            entity = Entity(
                id=entity_data.properties.get('id'),
                name=entity_data.properties.get('name'),
                label=entity_data.properties.get('label'),
                description=entity_data.properties.get('description'),
                vector=entity_data.properties.get('vector')
            )
            entities.entities.append(entity)
        return entities

    def search_entities(self, query: str, limit: int = 10) -> EntityList:
        """
        Search for entities based on a query string.

        Args:
            query: The search query string.
            limit: The maximum number of results to return.

        Returns:
            EntityList: A list of entities matching the search query.
        """
        cypher_query = (
            "MATCH (e:Entity) "
            "WHERE e.name CONTAINS $query OR e.description CONTAINS $query "
            "RETURN e "
            "LIMIT $limit"
        )
        params = {"query": query, "limit": limit}
        result = self.hybridstore.query(cypher_query, params=params)
        
        entities = EntityList()
        for row in result.result_set:
            entity_data = row[0]
            entity = Entity(
                id=entity_data.properties.get('id'),
                name=entity_data.properties.get('name'),
                label=entity_data.properties.get('label'),
                description=entity_data.properties.get('description'),
                vector=entity_data.properties.get('vector')
            )
            entities.entities.append(entity)
        return entities

    def update(self, entities_or_facts: Union[Entity, EntityList, Fact, FactList]) -> None:
        """
        Update or create entities or facts in the FalkorDB graph.

        This method serves as a dispatcher that determines whether to update entities or facts
        based on the type of input provided. It then calls the appropriate internal method
        to perform the update operation.

        Args:
            entities_or_facts (Union[Entity, EntityList, Fact, FactList]): 
                The entities or facts to update or create. Can be a single Entity or Fact,
                or a list of entities (EntityList) or facts (FactList).

        Raises:
            ValueError: If an invalid datatype is provided that is not Entity, EntityList, 
                        Fact, or FactList.

        Note:
            - For entities, it calls the _update_entities method.
            - For facts, it calls the _update_facts method.
            - Both methods handle the creation of new entries if they don't exist,
              or update existing ones if they do.
        """
        if isinstance(entities_or_facts, (Entity, EntityList)):
            self._update_entities(entities_or_facts)
        elif isinstance(entities_or_facts, (Fact, FactList)):
            self._update_facts(entities_or_facts)
        else:
            raise ValueError("Invalid datatype provided must be Entity or EntityList or Fact or FactList")

    def clear(self) -> None:
        """
        Clear all entities and facts from the FalkorDB graph.

        This method removes all entities and their relationships (facts) from the graph.
        It ensures that the entire graph is cleared of all data.
        """
        self.hybridstore.query("MATCH (n:Entity) DETACH DELETE n")
        self.hybridstore.query("MATCH (n:Fact) DETACH DELETE n")
        self.hybridstore.query("MATCH (n:Relationship) DETACH DELETE n")
        self.hybridstore.query("MATCH (n:GraphProgram) DETACH DELETE n")
        self.hybridstore.query("MATCH (n:UserProfile) DETACH DELETE n")
        self.hybridstore.query("MATCH (n:Message) DETACH DELETE n")
        self.hybridstore.query("MATCH ()-[r:RELATION]->() DELETE r")
    
    def remove(self, id_or_ids: Union[UUID, str, List[Union[UUID, str]]]) -> None:
        """
        Remove entities or facts from the FalkorDB graph.

        This method takes either a single ID or a list of IDs and removes the corresponding
        entities or facts from the graph. It handles both entity nodes and relationship (fact) removals.

        Args:
            id_or_ids (Union[UUID, str, List[Union[UUID, str]]]): 
                The ID or list of IDs of the entities or facts to remove. 
                Can be UUID objects or strings.

        Note:
            - For entities, it uses DETACH DELETE to remove the node and all its relationships.
            - For facts (relationships), it removes only the relationship, leaving the connected nodes intact.
            - The method uses separate queries for entity and fact removals to ensure correct execution.
            - If a list of IDs is provided, the removal operation is performed for each ID in the list.
        """
        ids = [str(id_or_ids)] if isinstance(id_or_ids, (UUID, str)) else [str(id) for id in id_or_ids]
        for id in ids:
            # Remove entity (if it exists)
            self.hybridstore.query(
                "MATCH (e:Entity {id: $id}) DETACH DELETE e",
                params={"id": id}
            )
            # Remove fact/relationship (if it exists)
            self.hybridstore.query(
                "MATCH ()-[r:RELATION {id: $id}]->() DELETE r",
                params={"id": id}
            )
