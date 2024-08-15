from collections import OrderedDict
import re
from typing import Union, List, Optional, Dict
from collections import OrderedDict
from uuid import UUID
import uuid
from ....embeddings.embeddings import Embeddings
from ....memory.program_memory import ProgramMemory
from .falkordb_memory import FalkorDBMemory
from ....core.graph_program import GraphProgram, Action, Decision, Program
from ....core.graph_program import GraphProgram, Action, Control, Decision, Program
from ....core.datatypes import GraphProgramList

RESERVED_NAMES = [
    "main",
    "playground",
    "filesystem",
    "program_memory",
    "trace_memory",
    "fact_memory",
    "\u006D\u0061\u0069\u006E",
    "\u0070\u006C\u0061\u0079\u0067\u0072\u006F\u0075\u006E\u0064",
    "\u0066\u0069\u006C\u0065\u0073\u0079\u0073\u0074\u0065\u006D",
    "\u0070\u0072\u006F\u0067\u0072\u0061\u006D\u005F\u006D\u0065\u006D\u006F\u0072\u0079",
    "\u0074\u0072\u0061\u0063\u0065\u005F\u006D\u0065\u006D\u006F\u0072\u0079",
]

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

    Attributes:
        _programs (Optional[Dict[str, GraphProgram]]): A dictionary to store programs. 
            The keys are program names and the values are GraphProgram objects.
        _embeddings (Optional[Dict[str, List[float]]]): An ordered dictionary to store program embeddings. 
            The keys are program names and the values are lists of floats representing the embeddings.
    """

    _programs: Optional[Dict[str, GraphProgram]] = {}
    _embeddings: Optional[Dict[str, List[float]]] = OrderedDict()

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
        entrypoint: str = "main",
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
        )
        self._programs = {}
        self._embeddings = OrderedDict()
        self._embeddings_model = embeddings
        self.schema = ""
        self.entrypoint = entrypoint
        
        if wipe_on_start:
            self.clear()

    def depends_on(self, source_id: Union[UUID, str], target_id: Union[UUID, str]) -> bool:
        """
        Check if the source program depends on the target program.

        Args:
            source_id (Union[UUID, str]): The ID of the source program.
            target_id (Union[UUID, str]): The ID of the target program.

        Returns:
            bool: True if the source program depends on the target program, False otherwise.
        """
        query = """
        MATCH (source:Program {name: $source_id})-[:DEPENDS_ON]->(target:Program {name: $target_id})
        RETURN COUNT(*) > 0 AS depends
        """
        result = self.hybridstore.query(query, params={"source_id": str(source_id), "target_id": str(target_id)})
        return result.result_set[0][0] if result.result_set else False

    def get_dependencies(self, prog_id: Union[UUID, str]) -> List[str]:
        """
        Get the dependencies of a program.

        Args:
            prog_id (Union[UUID, str]): The ID of the program.

        Returns:
            List[str]: A list of program IDs that the given program depends on.
        """
        query = """
        MATCH (p:Program {name: $prog_id})-[:DEPENDS_ON]->(dep:Program)
        RETURN dep.name AS dependency
        """
        result = self.hybridstore.query(query, params={"prog_id": str(prog_id)})
        return [row[0] for row in result.result_set] if result.result_set else []

    def exist(self, prog_id: Union[UUID, str], label: Optional[str] = None) -> bool:
        prog_name = str(prog_id)
        query = "MATCH (n:Program {name: $index}) RETURN COUNT(n) AS count"
        result = self.hybridstore.query(query, params={"index": prog_name})
        return result.result_set[0][0] > 0

    def update(self, prog_or_progs: Union[GraphProgram, GraphProgramList]) -> None:
        if isinstance(prog_or_progs, GraphProgram):
            programs = [prog_or_progs]
        elif isinstance(prog_or_progs, GraphProgramList):
            programs = prog_or_progs.progs
        else:
            raise ValueError("Invalid input type. Expected GraphProgram or GraphProgramList.")

        for prog in programs:
            prog.build()  # Ensure the program is built before updating
            
            # Update the internal dictionary
            self._programs[prog.name] = prog
            
            # Delete existing program
            self.hybridstore.query(
                "MATCH (p:Program {name: $name}) DETACH DELETE p",
                params={"name": prog.name}
            )
            
            # Create program node
            self.hybridstore.query(
                "CREATE (p:Program {name: $name, description: $description})",
                params={"name": prog.name, "description": prog.description or ""}
            )
            
            # Add steps
            for step_id, step in prog.steps.items():
                step_data = {
                    "id": step_id,
                    "type": type(step).__name__,
                    "tool": step.tool if isinstance(step, Action) else None,
                    "purpose": step.purpose if isinstance(step, (Action, Decision, Program)) else None,
                    "prompt": step.prompt if isinstance(step, Action) else None,
                    "question": step.question if isinstance(step, Decision) else None,
                    "program": step.program if isinstance(step, Program) else None,
                }
                self.hybridstore.query(
                    """
                    MATCH (p:Program {name: $prog_name})
                    CREATE (s:Step {id: $step_id, type: $type, tool: $tool, purpose: $purpose, prompt: $prompt, question: $question, program: $program})
                    CREATE (p)-[:HAS_STEP]->(s)
                    """,
                    params={
                        "prog_name": prog.name,
                        "step_id": step_id,
                        "type": step_data["type"],
                        "tool": step_data["tool"],
                        "purpose": step_data["purpose"],
                        "prompt": step_data["prompt"],
                        "question": step_data["question"],
                        "program": step_data["program"],
                    }
                )
                if isinstance(step, Program):
                    self.hybridstore.query(
                        """
                        MATCH (p:Program {name: $prog_name})-[:HAS_STEP]->(s:Step {id: $step_id})
                        MATCH (d:Program {name: $program})
                        MERGE (p)-[:DEPENDS_ON]->(d)
                        """,
                        params={
                            "prog_name": prog.name,
                            "step_id": step_id,
                            "program": step.program,
                        }
                    )
            
            # Add connections
            for source, targets in prog._graph.adj.items():
                for target in targets:
                    self.hybridstore.query(
                        """
                        MATCH (p:Program {name: $prog_name})-[:HAS_STEP]->(s1:Step {id: $source})
                        MATCH (p)-[:HAS_STEP]->(s2:Step {id: $target})
                        CREATE (s1)-[:NEXT]->(s2)
                        """,
                        params={
                            "prog_name": prog.name,
                            "source": source,
                            "target": target
                        }
                    )

    def remove(self, id_or_ids: Union[UUID, str, List[Union[UUID, str]]]) -> None:
        if isinstance(id_or_ids, (UUID, str)):
            program_names = [str(id_or_ids)]
        elif isinstance(id_or_ids, list):
            program_names = [str(id) for id in id_or_ids]
        else:
            raise ValueError("Invalid input type for id_or_ids")

        for prog_name in program_names:
            if prog_name in self._programs:
                del self._programs[prog_name]
            self.hybridstore.query(
                "MATCH (n:Program {name: $name}) DETACH DELETE n",
                params={"name": prog_name}
            )

    def get(self, id_or_ids: Union[UUID, str, List[Union[UUID, str]]]) -> GraphProgramList:
        if isinstance(id_or_ids, (UUID, str)):
            program_ids = [str(id_or_ids)]
        elif isinstance(id_or_ids, list):
            program_ids = [str(id) for id in id_or_ids]
        else:
            raise ValueError("Invalid input type for id_or_ids")

        programs = GraphProgramList(progs=[])
        
        for prog_id in program_ids:
            # Fetch program metadata
            result = self.hybridstore.query(
                "MATCH (p:Program {name: $name}) RETURN p.name, p.description",
                params={"name": prog_id}
            )
            
            if result.result_set:
                name, description = result.result_set[0]
                program = GraphProgram(name=name, description=description)
                
                # Fetch all steps excluding start and end
                steps_result = self.hybridstore.query(
                    '''
                    MATCH (p:Program {name: $name})-[:HAS_STEP]->(s)
                    WHERE s.id <> 'start' AND s.id <> 'end'
                    RETURN s.id, s.type, s.tool, s.purpose, s.prompt, s.question, s.program
                    ''',
                    params={"name": name}
                )
                
                for step in steps_result.result_set:
                    step_id, step_type, tool, purpose, prompt, question, program_name = step
                    if step_type == "Action":
                        action = Action(id=step_id, tool=tool, purpose=purpose, prompt=prompt)
                        program.add(action)
                    elif step_type == "Control":
                        control = Control(id=step_id)
                        program.add(control)
                    elif step_type == "Decision":
                        decision = Decision(id=step_id, purpose=purpose, question=question)
                        program.add(decision)
                    elif step_type == "Program":
                        prog = Program(id=step_id, purpose=purpose, program=program_name)
                        program.add(prog)
                
                # Fetch program structure (edges)
                edges_result = self.hybridstore.query(
                    '''
                    MATCH (p:Program {name: $name})-[:HAS_STEP]->(s1)-[:NEXT]->(s2)
                    RETURN s1.id, s2.id
                    ''',
                    params={"name": name}
                )
                
                for edge in edges_result.result_set:
                    source, target = edge
                    program.connect(source, target)
                
                # Fetch dependencies
                dependencies_result = self.hybridstore.query(
                    "MATCH (p:Program {name: $name})-[:DEPENDS_ON]->(d:Program) RETURN d.name AS dependency",
                    params={"name": name}
                )
                program.dependencies = [row[0] for row in dependencies_result.result_set] if dependencies_result.result_set else []
                
                programs.progs.append(program)
            else:
                print(f"No program found for ID: {prog_id}")

        return programs

    def is_protected(self, program_name: str):
        if program_name in RESERVED_NAMES:
            return True
        else:
            if self.depends_on("main", program_name):
                return True
        return False

    def clear(self):
        """
        Clears all program-related data from the FalkorDB memory.
        """
        super().clear()  # Call the clear method from FalkorDBMemory
        self.hybridstore.query("MATCH (p:Program) DETACH DELETE p")
        self.hybridstore.query(f"MATCH (c:{self.indexed_label}) DETACH DELETE c")

    def get_all_programs(self) -> GraphProgramList:
        """
        Retrieves all valid programs stored in the database.

        Returns:
            GraphProgramList: A list of all stored valid GraphProgram objects.
        """
        query = """
        MATCH (p:Program)
        RETURN p.name AS name, p.cypher AS cypher
        """
        result = self.hybridstore.query(query)

        programs = GraphProgramList(progs=[])
        if result and result.result_set:
            for row in result.result_set:
                if row and len(row) == 2:
                    name, cypher = row
                    program = GraphProgram(name=name)
                    if cypher is not None:
                        program.from_cypher(cypher)
                    program.build()
                    programs.progs.append(program)

        return programs
