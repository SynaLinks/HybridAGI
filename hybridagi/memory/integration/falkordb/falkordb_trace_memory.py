import uuid
import json
from typing import Union, List, Optional, Dict
from uuid import UUID
from collections import OrderedDict
from hybridagi.embeddings.embeddings import Embeddings
from hybridagi.memory.trace_memory import TraceMemory
from hybridagi.core.datatypes import AgentStep, AgentStepList, AgentStepType
from .falkordb_memory import FalkorDBMemory

DATETIME_FORMAT = r'%Y-%m-%d %H:%M:%S'

class FalkorDBTraceMemory(FalkorDBMemory, TraceMemory):
    """
    A class used to manage and store agent steps using FalkorDB.

    This class extends FalkorDBMemory and implements the TraceMemory interface,
    providing a robust solution for storing and managing agent steps in a graph database.
    It allows for efficient storage, retrieval, and manipulation of agent steps using
    FalkorDB's graph capabilities.
    """
    def __init__(
        self,
        index_name: str,
        graph_index: str = "trace_memory",
        hostname: str = "localhost",
        port: int = 6379,
        username: str = "",
        password: str = "",
        wipe_on_start: bool = False,
        **kwargs
    ):
        super().__init__(
            index_name=index_name,
            graph_index=graph_index,
            hostname=hostname,
            port=port,
            username=username,
            password=password,
            wipe_on_start=wipe_on_start,
            **kwargs
        )

    def exist(self, step_id: Union[UUID, str]) -> bool:
        """
        Check if an agent step exists by its ID.

        Args:
            step_id: The ID of the agent step to check for existence.

        Returns:
            bool: True if the agent step exists, False otherwise.
        """
        return super().exist(step_id, "AgentStep")

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
        if not isinstance(step_or_steps, (AgentStep, AgentStepList)):
            raise ValueError("Invalid datatype provided must be AgentStep or AgentStepList")
        if isinstance(step_or_steps, AgentStep):
            steps = AgentStepList()
            steps.steps = [step_or_steps]
        else:
            steps = step_or_steps
        for step in steps.steps:
            step_id = str(step.id)
            if step.vector is not None:
                params = {
                    "id": step_id,
                    "parent_id": str(step.parent_id) if step.parent_id else None,
                    "hop": step.hop,
                    "step_type": step.step_type.value,
                    "inputs": json.dumps(step.inputs) if step.inputs else "{}",
                    "outputs": json.dumps(step.outputs) if step.inputs else "{}",
                    "vector": list(step.vector) if step.vector is not None else None,
                    "metadata": json.dumps(step.metadata),
                    "created_at": step.created_at.strftime(DATETIME_FORMAT),
                }
                self._graph.query(
                    " ".join([
                    "MERGE (s:AgentStep {id: $id})",
                    "SET",
                    "s.parent_id=$parent_id,",
                    "s.hop=$hop,",
                    "s.step_type=$step_type,",
                    "s.inputs=$inputs,",
                    "s.outputs=$outputs,",
                    "s.vector=vecf32($vector),",
                    "s.metadata=$metadata,",
                    "s.created_at=$created_at"]),
                    params = params,
                )
            if step.parent_id is not None:
                parent_id = str(step.parent_id)
                params = {
                    "id": step_id,
                    "parent_id": parent_id,
                }
                self._graph.query(
                    "MATCH (child:AgentStep {id: $id}), (parent:AgentStep {id: $parent_id}) MERGE (parent)-[:NEXT]->(child)",
                    params = params,
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
        result = self._graph.query(
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