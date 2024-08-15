from typing import Union, List
from uuid import UUID
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
        self.schema = ""

    def exist(self, step_id) -> bool:
        """
        Check if an agent step exists by its ID.

        Args:
            step_id: The ID of the agent step to check for existence.

        Returns:
            bool: True if the agent step exists, False otherwise.
        """
        return self.exists(str(step_id), label="AgentStep")

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
            params = {
                "id": str(step.id),
                "step_type": step.step_type.value,
                "parent_id": str(step.parent_id) if step.parent_id else None,
                "vector": list(step.vector) if step.vector is not None else None,
                "name": step.name,
                "description": step.description
            }
            self.hybridstore.query(
                "MERGE (s:AgentStep {id: $id}) "
                "SET s.step_type = $step_type, s.vector = $vector, s.name = $name, s.description = $description",
                params=params
            )
            if step.parent_id:
                self.hybridstore.query(
                    "MATCH (s:AgentStep {id: $id}), (p:AgentStep {id: $parent_id}) "
                    "MERGE (s)-[:NEXT]->(p)",
                    params=params
                )

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
            "RETURN s.id, s.step_type, s.parent_id, s.vector",
            params={"ids": ids}
        )
        steps = AgentStepList()
        for row in result.result_set:
            step = AgentStep(
                id=UUID(row[0]),
                step_type=AgentStepType(row[1]),
                parent_id=UUID(row[2]) if row[2] else None,
                vector=row[3]
            )
            steps.steps.append(step)
        return steps

    def get_trace(self, step_id: Union[UUID, str]) -> AgentStepList:
        """
        Retrieve the trace of agent steps starting from a specific step ID.

        This method fetches the sequence of agent steps that follow the specified step ID.

        Args:
            step_id (Union[UUID, str]): The ID of the agent step to start the trace from.

        Returns:
            AgentStepList: A list of AgentStep objects representing the trace of agent steps.
        """
        result = self.hybridstore.query(
            "MATCH (s:AgentStep {id: $id})-[:NEXT*]->(p:AgentStep) "
            "RETURN p.id, p.step_type, p.parent_id, p.vector",
            params={"id": str(step_id)}
        )
        steps = AgentStepList()
        for row in result.result_set:
            step = AgentStep(
                id=UUID(row[0]),
                step_type=AgentStepType(row[1]),
                parent_id=UUID(row[2]) if row[2] else None,
                vector=row[3]
            )
            steps.steps.append(step)
        return steps

    def clear(self):
        """
        Remove all agent steps from the database.

        This method deletes all AgentStep nodes and their relationships from the graph database.

        Note:
            - This operation is irreversible and will delete all agent step data.
            - Use with caution as it will empty the entire agent step store.
        """
        self.hybridstore.query("MATCH (s:AgentStep) DETACH DELETE s", params={})
