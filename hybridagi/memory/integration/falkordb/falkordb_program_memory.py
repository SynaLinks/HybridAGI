import json
from typing import Union, List, Optional, Dict
from uuid import UUID
from ....memory.program_memory import ProgramMemory
from .falkordb_memory import FalkorDBMemory
from ....core.graph_program import GraphProgram
from ....core.datatypes import GraphProgramList

class FalkorDBProgramMemory(FalkorDBMemory, ProgramMemory):
    """
    Manages and stores programs using FalkorDB.

    This class extends FalkorDBMemory and implements the ProgramMemory interface,
    providing a solution for storing and managing programs in a graph database.
    It allows for efficient storage, retrieval, and manipulation of programs using
    FalkorDB's graph capabilities.
    """

    def __init__(
        self,
        index_name: str,
        graph_index: str = "program_memory",
        hostname: str = "localhost",
        port: int = 6379,
        username: str = "",
        password: str = "",
        wipe_on_start: bool = False,
    ):
        super().__init__(
            index_name=index_name,
            graph_index=graph_index,
            hostname=hostname,
            port=port,
            username=username,
            password=password,
            wipe_on_start=wipe_on_start,
        )
        if wipe_on_start:
            self.clear()
            
    def exist(self, prog_id: Union[UUID, str]) -> bool:
        return super().exist(prog_id, "Program")
    
    def update(self, program_or_programs: Union[GraphProgram, GraphProgramList]) -> None:
        """
        Update falkorDB program memory with new programs.

        Parameters:
            program_or_programs (Union[GraphProgram, GraphProgramList]): A single program or a list of programs to be added to the memory.

        Raises:
            ValueError: If the input is not a GraphProgram or GraphProgramList.
        
        Note:
            - If a program with the given ID already exists, it will be updated.
            - If a program with the given ID doesn't exist, a new one will be created.
            - For programs with dependencies, a DEPENDS_ON relationship is created or updated.
            - Program metadata is stored as properties on the Program node.
        """
        if not isinstance(program_or_programs, (GraphProgram, GraphProgramList)):
            raise ValueError("Invalid datatype provided must be GraphProgram or GraphProgramList")
        if isinstance(program_or_programs, GraphProgram):
            programs = GraphProgramList()
            programs.progs = [program_or_programs]
        else:
            programs = program_or_programs
        for prog in programs.progs:
            prog_id = str(prog.name)
            params = {
                "id": prog_id,
                "program": prog.to_cypher(),
                "vector": list(prog.vector) if prog.vector is not None else None,
                "metadata": json.dumps(prog.metadata)
            }
            self._graph.query(
                " ".join([
                "MERGE (p:Program {id: $id})",
                "SET p.program=$program,",
                "p.metadata=$metadata,",
                "p.vector=vecf32($vector)"]),
                params = params,
            )
            params = {
                "id": prog_id,
            }
            self._graph.query(
                "MATCH (:Program {id: $id})-[r]->() DELETE r",
                params=params,
            )
            for dep in prog.dependencies:
                params = {
                    "id": prog_id,
                    "dep": dep,
                }
                self._graph.query(
                    "MATCH (p:Program {id: $id}) MERGE (p)-[:DEPENDS_ON]->(:Program {id: $dep})",
                    params = params,
                )
                
    def remove(self, id_or_ids: Union[UUID, str, List[Union[UUID, str]]]) -> None:
        """
        Remove programs from the falkorDB program memory.

        Parameters:
            id_or_ids (Union[UUID, str, List[Union[UUID, str]]]): A single program id or a list of program ids to be removed from the memory.
        """
        if not isinstance(id_or_ids, list):
            programs_ids = [id_or_ids]
        else:
            programs_ids = id_or_ids
        for prog_id in programs_ids:
            prog_id = str(prog_id)
            self._graph.query(
                "MATCH (n:Program {id: $id}) DETACH DELETE n",
                params={"id": prog_id}
            )
                
    def get(self, id_or_ids: Union[UUID, str, List[Union[UUID, str]]]) -> GraphProgramList:
        """
        Retrieve programs from the falkorDB program memory.

        Parameters:
            id_or_ids (Union[UUID, str, List[Union[UUID, str]]]): A single program id or a list of program ids to be retrieved from the memory.

        Returns:
            GraphProgramList: A list of programs that match the input ids.
        """
        if not isinstance(id_or_ids, list):
            programs_ids = [id_or_ids]
        else:
            programs_ids = id_or_ids
        result = GraphProgramList()
        for prog_id in programs_ids:
            prog_id = str(prog_id)
            if self.exist(prog_id):
                query_result = self._graph.query(
                    "MATCH (p:Program {id: $id}) RETURN p",
                    params={"id": prog_id}
                )
                cypher_program = query_result.result_set[0][0].properties["program"]
                metadata = query_result.result_set[0][0].properties["metadata"]
                prog = GraphProgram(name=prog_id)
                prog.from_cypher(cypher_program)
                prog.metadata = json.loads(metadata)
                if "vector" in query_result.result_set[0][0].properties:
                    prog.vector = query_result.result_set[0][0].properties["vector"]
                result.progs.append(prog)
        return result

    def get_dependencies(self, prog_id: Union[UUID, str]) -> List[str]:
        """
        Get the dependencies of a program.

        Args:
            prog_id (Union[UUID, str]): The ID of the program.

        Returns:
            List[str]: A list of program IDs that the given program depends on.
        """
        if not self.exist(str(prog_id)):
            raise ValueError(f"GraphProgram {prog_id} does not exist.")
        programs = self.get(str(prog_id))
        prog = programs.progs[0]
        return prog.dependencies
    
    def depends_on(self, source_id: Union[UUID, str], target_id: Union[UUID, str]) -> bool:
        """
        Check if the source program depends on the target program.

        Args:
            source_id (Union[UUID, str]): The ID of the source program.
            target_id (Union[UUID, str]): The ID of the target program.

        Returns:
            bool: True if the source program depends on the target program, False otherwise.
        """
        params = {"source": str(source_id), "target": str(target_id)}
        result = self._graph.query(
            "MATCH (n:Program {id:$source})-[r:DEPENDS_ON*]->(m:Program {id:$target}) RETURN r",
            params = params,
        )
        print(result.result_set)
        if len(result.result_set) > 0:
            return True
        return False
    
    def is_protected(self, program_name: str):
        if program_name == "main":
            return True
        else:
            if self.depends_on("main", program_name):
                return True
        return False