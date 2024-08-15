from typing import Union, List
from uuid import UUID
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
        graph_index: str = "trace_memory", 
        wipe_on_start: bool = True, 
        *args, 
        **kwargs
        ):
        super().__init__(
            index_name=index_name, 
            graph_index=graph_index, 
            wipe_on_start=wipe_on_start, 
            *args, 
            **kwargs
        )

    def exist(self, step_id) -> bool:
        return self.exists(str(step_id), label="AgentStep")

    def update(self, step_or_steps: Union[AgentStep, AgentStepList]) -> None:
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
                "vector": list(step.vector) if step.vector is not None else None
            }
            self.hybridstore.query(
                "MERGE (s:AgentStep {id: $id}) "
                "SET s.step_type = $step_type, s.vector = $vector",
                params=params
            )
            if step.parent_id:
                self.hybridstore.query(
                    "MATCH (s:AgentStep {id: $id}), (p:AgentStep {id: $parent_id}) "
                    "MERGE (s)-[:NEXT]->(p)",
                    params=params
                )

    def remove(self, id_or_ids: Union[UUID, str, List[Union[UUID, str]]]) -> None:
        ids = [str(id_or_ids)] if isinstance(id_or_ids, (UUID, str)) else [str(id) for id in id_or_ids]
        for id in ids:
            self.hybridstore.query(
                "MATCH (s:AgentStep {id: $id}) DETACH DELETE s",
                params={"id": id}
            )

    def get(self, id_or_ids: Union[UUID, str, List[Union[UUID, str]]]) -> AgentStepList:
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
        self.hybridstore.query("MATCH (n:AgentStep) DETACH DELETE n")
