import uuid
import json
from typing import Union, List, Optional, Dict
from uuid import UUID
from collections import OrderedDict
from hybridagi.embeddings.embeddings import Embeddings
from hybridagi.memory.trace_memory import TraceMemory
from hybridagi.core.datatypes import AgentStep, AgentStepList, AgentStepType
from .falkordb_memory import FalkorDBMemory

class FalkorDBTraceMemory(FalkorDBMemory, TraceMemory):
    """
    A class used to manage and store agent steps using FalkorDB.

    This class extends FalkorDBMemory and implements the TraceMemory interface,
    providing a robust solution for storing and managing agent steps in a graph database.
    It allows for efficient storage, retrieval, and manipulation of agent steps using
    FalkorDB's graph capabilities.

    Key features:
    1. Step management: Store and retrieve agent steps with their properties.
    2. Efficient querying: Utilize FalkorDB's graph querying capabilities for fast data retrieval.
    3. Vector embeddings: Support for storing and querying vector embeddings of agent steps.
    4. CRUD operations: Implement create, read, update, and delete operations for agent steps.

    This implementation provides a scalable and flexible solution for trace-based
    knowledge representation in AI and machine learning applications.
    """

    _steps: Optional[Dict[str, AgentStep]] = {}
    _embeddings: Optional[Dict[str, List[float]]] = OrderedDict()

    def __init__(
        self,
        index_name: str,
        embeddings: Embeddings,
        graph_index: str = "trace_memory",
        hostname: str = "localhost",
        port: int = 6379,
        username: str = "",
        password: str = "",
        indexed_label: str = "Content",
        wipe_on_start: bool = False,
        **kwargs
    ):
        super().__init__(
            index_name=index_name,
            graph_index=graph_index,
            embeddings=embeddings,
            hostname=hostname,
            port=port,
            username=username,
            password=password,
            indexed_label=indexed_label,
            wipe_on_start=wipe_on_start,
            **kwargs
        )
        self.current_commit = None
        self._steps = {}
        self._embeddings = OrderedDict()

    def exist(self, step_id: Union[UUID, str]) -> bool:
        """
        Check if an agent step exists by its ID.

        Args:
            step_id: The ID of the agent step to check for existence.

        Returns:
            bool: True if the agent step exists, False otherwise.
        """
        # Convert step_id to string if it's a UUID
        step_id_str = str(step_id)
        
        # Check for existence specific to AgentStep
        query = "MATCH (s:AgentStep {id: $id}) RETURN COUNT(s) > 0 AS exists"
        params = {"id": step_id_str}
        result = self.hybridstore.query(query, params=params)
        
        return result.result_set[0][0] if result.result_set else False

    def update(self, step_or_steps: Union[AgentStep, AgentStepList]) -> None:
        """
        Update an agent step or a list of agent steps in the database.

        This method updates existing agent steps or creates new ones if they don't exist.
        It handles both individual AgentStep objects and AgentStepList objects.

        Args:
            step_or_steps (Union[AgentStep, AgentStepList]): The agent step(s) to update or create.

        Raises:
            ValueError: If the input is neither an AgentStep nor an AgentStepList.
        """
        if isinstance(step_or_steps, AgentStep):
            steps = AgentStepList(steps=[step_or_steps])
        elif isinstance(step_or_steps, AgentStepList):
            steps = step_or_steps
        else:
            raise ValueError("Invalid datatype provided must be AgentStep or AgentStepList")

        for step in steps.steps:
            step_id = str(step.id)
            params = {
                "id": step_id,
                "step_type": step.step_type.value,
                "vector": list(step.vector) if step.vector is not None else None,
                "name": step.name,
                "description": step.description,
                "parent_id": str(step.parent_id) if step.parent_id else None
            }
            
            # Create or update the step
            self.hybridstore.query(
                "MERGE (s:AgentStep {id: $id}) "
                "SET s.step_type = $step_type, s.vector = $vector, s.name = $name, s.description = $description",
                params=params
            )
            
            # Create parent-child relationship if parent exists
            if params["parent_id"]:
                self.hybridstore.query(
                    "MATCH (parent:AgentStep {id: $parent_id}), (child:AgentStep {id: $id}) "
                    "MERGE (parent)-[:NEXT]->(child)",
                    params=params
                )
            
            # Update local cache
            self._steps[step_id] = step
            if step.vector is not None:
                self._embeddings[step_id] = step.vector

    def remove(self, id_or_ids: Union[UUID, str, List[Union[UUID, str]]]) -> None:
        """
        Remove an agent step or a list of agent steps by their IDs.

        This method deletes agent steps with the specified ID(s) from the database.
        It can handle a single ID or a list of IDs.

        Args:
            id_or_ids (Union[UUID, str, List[Union[UUID, str]]]): The ID(s) of the agent step(s) to remove.
                Can be a single UUID, string, or a list of UUIDs or strings.
        """
        ids = [str(id_or_ids)] if isinstance(id_or_ids, (UUID, str)) else [str(id) for id in id_or_ids]
        for id in ids:
            self.hybridstore.query(
                "MATCH (s:AgentStep {id: $id}) DETACH DELETE s",
                params={"id": id}
            )

    def get(self, id_or_ids: Union[UUID, str, List[Union[UUID, str]]]) -> AgentStepList:
        """
        Retrieve an agent step or a list of agent steps by their IDs.

        This method fetches agent steps with the specified ID(s) from the database.
        It can handle a single ID or a list of IDs.

        Args:
            id_or_ids (Union[UUID, str, List[Union[UUID, str]]]): The ID(s) of the agent step(s) to retrieve.
                Can be a single UUID, string, or a list of UUIDs or strings.

        Returns:
            AgentStepList: A list of AgentStep objects matching the given ID(s).
        """
        ids = [str(id_or_ids)] if isinstance(id_or_ids, (UUID, str)) else [str(id) for id in id_or_ids]
        result = self.hybridstore.query(
            "MATCH (s:AgentStep) WHERE s.id IN $ids "
            "RETURN s.id, s.step_type, s.parent_id, s.vector, s.name, s.description",
            params={"ids": ids}
        )
        steps = AgentStepList()
        for row in result.result_set:
            step = AgentStep(
                id=UUID(row[0]),
                step_type=AgentStepType(row[1]),
                parent_id=UUID(row[2]) if row[2] is not None else None,
                vector=row[3],
                name=row[4],
                description=row[5]
            )
            steps.steps.append(step)
        return steps

    def get_trace(self, step_id: Union[UUID, str]) -> AgentStepList:
        """
        Retrieve the trace of agent steps starting from a specific step ID.

        This method fetches the sequence of agent steps that lead to the specified step ID.

        Args:
            step_id (Union[UUID, str]): The ID of the agent step to end the trace at.

        Returns:
            AgentStepList: A list of AgentStep objects representing the trace of agent steps.

        Raises:
            Exception: If there's an error in retrieving the trace.
        """
        step_id_str = str(step_id)
        query = """
        MATCH (step:AgentStep {id: $step_id})
        MATCH (step)<-[:NEXT*0..]-(ancestor:AgentStep)
        RETURN ancestor.id, ancestor.step_type, ancestor.parent_id, ancestor.vector, ancestor.name, ancestor.description
        ORDER BY length((ancestor)-[:NEXT*]->(step)) DESC
        """
        result = self.hybridstore.query(query, params={"step_id": step_id_str})
        
        steps = AgentStepList()
        for row in result.result_set:
            step = AgentStep(
                id=UUID(row[0]),
                step_type=AgentStepType(row[1]),
                parent_id=UUID(row[2]) if row[2] else None,
                vector=row[3],
                name=row[4],
                description=row[5]
            )
            steps.steps.append(step)
        
        return steps

    def add(self, step: AgentStep) -> None:
        """
        Add a new agent step to the database.

        Args:
            step (AgentStep): The agent step to add.
        """
        if step.inputs is None:
            step.inputs = {}
        if "purpose" not in step.inputs:
            step.inputs["purpose"] = "Not specified"
        self.update(step)

    def add_many(self, steps: AgentStepList) -> None:
        """
        Add multiple agent steps to the database.

        Args:
            steps (AgentStepList): The list of agent steps to add.
        """
        for step in steps.steps:
            if step.inputs is None:
                step.inputs = {}
            if "purpose" not in step.inputs:
                step.inputs["purpose"] = "Not specified"
        self.update(steps)

    def search(self, query: str, k: int = 10) -> AgentStepList:
        """
        Search for agent steps based on a query string.

        Args:
            query (str): The search query.
            k (int): The number of results to return.

        Returns:
            AgentStepList: A list of AgentStep objects matching the search query.
        """
        result = self.hybridstore.query(
            "MATCH (s:AgentStep) "
            "WHERE s.name CONTAINS $query OR s.description CONTAINS $query "
            "RETURN s.id, s.step_type, s.parent_id, s.vector, s.name, s.description "
            "LIMIT $k",
            params={"query": query, "k": k}
        )
        steps = AgentStepList()
        for row in result.result_set:
            step = AgentStep(
                id=UUID(row[0]),
                step_type=AgentStepType(row[1]),
                parent_id=UUID(row[2]) if row[2] else None,
                vector=row[3],
                name=row[4],
                description=row[5]
            )
            steps.steps.append(step)
        return steps

    def clear(self) -> None:
        """
        Clear all agent steps from the database and local cache.
        """
        # Clear FalkorDB
        self.hybridstore.query("MATCH (s:AgentStep) DETACH DELETE s")
        
        # Clear local cache
        self._steps = {}
        self._embeddings = OrderedDict()
        
        # Call parent class clear method
        super().clear()

    def get_schema(self) -> Optional[str]:
        """
        Get the schema of the trace memory.

        Returns:
            Optional[str]: The schema of the trace memory, if available.
        """
        return self.schema

    def set_schema(self, schema: str) -> None:
        """
        Set the schema of the trace memory.

        Args:
            schema (str): The schema to set for the trace memory.
        """
        self.schema = schema

    def get_schema(self) -> Optional[str]:
        """
        Get the schema of the trace memory.

        Returns:
            Optional[str]: The schema of the trace memory, if available.
        """
        return self.schema

    def set_schema(self, schema: str) -> None:
        """
        Set the schema of the trace memory.

        Args:
            schema (str): The schema to set for the trace memory.
        """
        self.schema = schema

    def start_new_trace(self):
        """Start a new trace"""
        self.current_commit = None

    def get_trace_indexes(self) -> List[str]:
        """Get the traces indexes (the first commit index of each trace)"""
        trace_indexes = []
        result = self.hybridstore.query('MATCH (n:ProgramCall {program:"main"}) RETURN n.name as name')
        for record in result.result_set:
            trace_indexes.append(record[0])
        return trace_indexes

    def is_finished(self, trace_index: str) -> bool:
        """Returns True if the execution of the program terminated"""
        params = {"index": trace_index}
        result = self.hybridstore.query(
            'MATCH (n:ProgramCall {name:$index, program:"main"})'
            +'-[:NEXT*]->(m:ProgramEnd {program:"main"}) RETURN m',
            params=params,
        )
        return len(result.result_set) > 0

    def get_full_trace(self) -> AgentStepList:
        """
        Retrieve the full trace of agent steps.

        Returns:
            AgentStepList: A list of all AgentStep objects in the trace, ordered by their relationships.
        """
        result = self.hybridstore.query(
            "MATCH (s:AgentStep) "
            "RETURN s.id, s.step_type, s.parent_id, s.vector, s.name, s.description "
            "ORDER BY s.id"
        )
        steps = AgentStepList()
        for row in result.result_set:
            step = AgentStep(
                id=UUID(row[0]),
                step_type=AgentStepType(row[1]),
                parent_id=UUID(row[2]) if row[2] else None,
                vector=row[3],
                name=row[4],
                description=row[5]
            )
            steps.steps.append(step)
        return steps
