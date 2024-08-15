from typing import Union, List
from uuid import UUID
from hybridagi.embeddings.embeddings import Embeddings
from hybridagi.memory.program_memory import ProgramMemory
from hybridagi.core.graph_program import GraphProgram
from hybridagi.core.datatypes import GraphProgramList
from .falkordb_memory import FalkorDBMemory

class FalkorDBProgramMemory(FalkorDBMemory, ProgramMemory):
    """
    Manages and stores programs using FalkorDB.

    This class extends FalkorDBMemory and implements the ProgramMemory interface,
    providing a solution for storing and managing programs in a graph database.
    It allows for efficient storage, retrieval, and manipulation of programs using
    FalkorDB's graph capabilities.

    Key features:
    1. Store and retrieve programs with their properties.
    2. Utilize graph querying capabilities for fast data retrieval.
    3. Support for storing and querying vector embeddings of programs.
    4. Implement create, read, update, and delete operations for programs.
    """
    def __init__(
        self,
        index_name: str,
        embeddings: Embeddings,
        graph_index: str = "program_memory",
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

    def exist(self, prog_id) -> bool:
        """
        Check if a program exists by its ID.

        Args:
            prog_id: The ID of the program to check for existence.

        Returns:
            bool: True if the program exists, False otherwise.
        """
        return self.exists(str(prog_id), label="Program")

    def update(self, program_or_programs: Union[GraphProgram, GraphProgramList]) -> None:
        """
        Update a program or a list of programs in the database.

        This method updates existing programs or creates new ones if they don't exist.
        It handles both individual GraphProgram objects and GraphProgramList objects.

        Args:
            program_or_programs (Union[GraphProgram, GraphProgramList]): The program(s) to update or create.

        Raises:
            ValueError: If the input is neither a GraphProgram nor a GraphProgramList.
        """
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
        """
        Remove a program or a list of programs by their IDs.

        This method deletes programs with the specified ID(s) from the database.
        It can handle a single ID or a list of IDs.

        Args:
            id_or_ids (Union[UUID, str, List[Union[UUID, str]]]): The ID(s) of the program(s) to remove.
                Can be a single UUID, string, or a list of UUIDs or strings.
        """
        ids = [str(id_or_ids)] if isinstance(id_or_ids, (UUID, str)) else [str(id) for id in id_or_ids]
        for id in ids:
            self.hybridstore.query(
                "MATCH (p:Program {id: $id}) DETACH DELETE p",
                params={"id": id}
            )

    def get(self, id_or_ids: Union[UUID, str, List[Union[UUID, str]]]) -> GraphProgramList:
        """
        Retrieve a program or a list of programs by their IDs.

        This method fetches programs with the specified ID(s) from the database.
        It can handle a single ID or a list of IDs.

        Args:
            id_or_ids (Union[UUID, str, List[Union[UUID, str]]]): The ID(s) of the program(s) to retrieve.
                Can be a single UUID, string, or a list of UUIDs or strings.

        Returns:
            GraphProgramList: A list of GraphProgram objects matching the given ID(s).
        """
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
        """
        Get a list of IDs for programs that the specified program depends on.

        Args:
            prog_id (Union[UUID, str]): The ID of the program to check dependencies for.

        Returns:
            List[str]: A list of IDs for programs that the specified program depends on.
        """
        result = self.hybridstore.query(
            "MATCH (p:Program {id: $id})-[:DEPENDS_ON]->(d:Program) "
            "RETURN d.id",
            params={"id": str(prog_id)}
        )
        return [row[0] for row in result.result_set]

    def depends_on(self, source_id: Union[UUID, str], target_id: Union[UUID, str]) -> bool:
        """
        Check if a program depends on another program.

        Args:
            source_id (Union[UUID, str]): The ID of the source program.
            target_id (Union[UUID, str]): The ID of the target program.

        Returns:
            bool: True if the source program depends on the target program, False otherwise.
        """
        result = self.hybridstore.query(
            "MATCH (p:Program {id: $source_id})-[:DEPENDS_ON*]->(d:Program {id: $target_id}) "
            "RETURN d.id",
            params={"source_id": str(source_id), "target_id": str(target_id)}
        )
        return len(result.result_set) > 0

    def clear(self):
        """
        Remove all programs from the database.

        This method deletes all Program nodes and their relationships from the graph database.

        Note:
            - This operation is irreversible and will delete all program data.
            - Use with caution as it will empty the entire program store.
        """
        self.hybridstore.query("MATCH (p:Program) DETACH DELETE p", params={})
