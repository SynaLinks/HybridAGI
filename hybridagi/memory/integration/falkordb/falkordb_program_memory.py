from typing import Union, List
from uuid import UUID
from hybridagi.memory.program_memory import ProgramMemory
from hybridagi.core.graph_program import GraphProgram
from hybridagi.core.datatypes import GraphProgramList
from .falkordb_memory import FalkorDBMemory

class FalkorDBProgramMemory(FalkorDBMemory, ProgramMemory):
    """
    A class used to manage and store programs using FalkorDB.

    This class extends FalkorDBMemory and implements the ProgramMemory interface,
    providing a robust solution for storing and managing programs in a graph database.
    It allows for efficient storage, retrieval, and manipulation of programs using
    FalkorDB's graph capabilities.

    Key features:
    1. Program management: Store and retrieve programs with their properties.
    2. Efficient querying: Utilize FalkorDB's graph querying capabilities for fast data retrieval.
    3. Vector embeddings: Support for storing and querying vector embeddings of programs.
    4. CRUD operations: Implement create, read, update, and delete operations for programs.

    This implementation provides a scalable and flexible solution for program-based
    knowledge representation in AI and machine learning applications.
    """
    def __init__(
        self, 
        index_name: str, 
        graph_index: str = "program_memory", 
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

    def exist(self, prog_id) -> bool:
        return self.exists(str(prog_id), label="Program")

    def update(self, program_or_programs: Union[GraphProgram, GraphProgramList]) -> None:
        if isinstance(program_or_programs, GraphProgram):
            programs = GraphProgramList(progs=[program_or_programs])
        elif isinstance(program_or_programs, GraphProgramList):
            programs = program_or_programs
        else:
            raise ValueError("Invalid datatype provided must be GraphProgram or GraphProgramList")

        for prog in programs.progs:
            params = {
                "id": str(prog.id),
                "name": prog.name,
                "vector": list(prog.vector) if prog.vector is not None else None
            }
            self.hybridstore.query(
                "MERGE (p:Program {id: $id}) "
                "SET p.name = $name, p.vector = $vector",
                params=params
            )
            for dep in prog.dependencies:
                self.hybridstore.query(
                    "MATCH (p:Program {id: $id}), (d:Program {id: $dep_id}) "
                    "MERGE (p)-[:DEPENDS_ON]->(d)",
                    params={"id": str(prog.id), "dep_id": str(dep)}
                )

    def remove(self, id_or_ids: Union[UUID, str, List[Union[UUID, str]]]) -> None:
        ids = [str(id_or_ids)] if isinstance(id_or_ids, (UUID, str)) else [str(id) for id in id_or_ids]
        for id in ids:
            self.hybridstore.query(
                "MATCH (p:Program {id: $id}) DETACH DELETE p",
                params={"id": id}
            )

    def get(self, id_or_ids: Union[UUID, str, List[Union[UUID, str]]]) -> GraphProgramList:
        ids = [str(id_or_ids)] if isinstance(id_or_ids, (UUID, str)) else [str(id) for id in id_or_ids]
        result = self.hybridstore.query(
            "MATCH (p:Program) WHERE p.id IN $ids "
            "RETURN p.id, p.name, p.vector",
            params={"ids": ids}
        )
        programs = GraphProgramList()
        for row in result.result_set:
            prog = GraphProgram(
                id=UUID(row[0]),
                name=row[1],
                vector=row[2]
            )
            programs.progs.append(prog)
        return programs

    def get_dependencies(self, prog_id: Union[UUID, str]) -> List[str]:
        result = self.hybridstore.query(
            "MATCH (p:Program {id: $id})-[:DEPENDS_ON]->(d:Program) "
            "RETURN d.id",
            params={"id": str(prog_id)}
        )
        return [row[0] for row in result.result_set]

    def depends_on(self, source_id: Union[UUID, str], target_id: Union[UUID, str]) -> bool:
        result = self.hybridstore.query(
            "MATCH (p:Program {id: $source_id})-[:DEPENDS_ON*]->(d:Program {id: $target_id}) "
            "RETURN d.id",
            params={"source_id": str(source_id), "target_id": str(target_id)}
        )
        return len(result.result_set) > 0

    def clear(self):
        self.hybridstore.query("MATCH (n:Program) DETACH DELETE n")
