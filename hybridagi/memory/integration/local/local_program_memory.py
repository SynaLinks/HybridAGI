from typing import Union, List, Dict, Optional
from uuid import UUID
from collections import OrderedDict
from hybridagi.memory.program_memory import ProgramMemory
from hybridagi.core.graph_program import GraphProgram
from hybridagi.core.datatypes import GraphProgramList
import networkx as nx

from .local_memory import LocalMemory

class LocalProgramMemory(LocalMemory, ProgramMemory):
    """
    A class used to manage and store programs locally.

    Attributes:
        index_name (str): The name of the index used for program storage.
        wipe_on_start (bool): Whether to clear the memory when the object is initialized.
        _programs (Optional[Dict[str, GraphProgram]]): A dictionary to store programs. The keys are program names and the values are GraphProgram objects.
        _embeddings (Optional[Dict[str, List[float]]]): An ordered dictionary to store program embeddings. The keys are program names and the values are lists of floats representing the embeddings.
        _graph (nx.DiGraph): A directed graph to store the dependencies between programs.
    """
    index_name: str
    wipe_on_start: bool
    _programs: Optional[Dict[str, GraphProgram]] = {}
    _embeddings: Optional[Dict[str, List[float]]] = OrderedDict()
    _graph: nx.DiGraph()
    
    def __init__(
            self,
            index_name: str,
            wipe_on_start: bool=True,
        ):
        """
        Initialize the local program memory.

        Parameters:
            index_name (str): The name of the index used for program storage.
            wipe_on_start (bool): Whether to clear the memory when the object is initialized.
        """
        self.index_name = index_name
        if wipe_on_start:
            self.clear()
            
    def exist(self, prog_id) -> bool:
        return prog_id in self._programs
    
    def update(self, program_or_programs: Union[GraphProgram, GraphProgramList]) -> None:
        """
        Update the local program memory with new programs.

        Parameters:
            program_or_programs (Union[GraphProgram, GraphProgramList]): A single program or a list of programs to be added to the memory.

        Raises:
            ValueError: If the input is not a GraphProgram or GraphProgramList.
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
            if prog_id not in self._programs:
                self._graph.add_node(prog_id, title=prog.to_cypher(), color="orange" if prog.name == "main" else "green")
            else:
                self._graph.nodes[prog_id]["title"] = prog.to_cypher()
            self._programs[prog_id] = prog
            if prog.vector is not None:
                self._embeddings[prog_id] = prog.vector
            previous_edges = self._graph.out_edges(prog_id)
            self._graph.remove_edges_from(previous_edges)
            for dep in prog.dependencies:
                self._graph.add_edge(prog_id, dep, label="DEPENDS_ON")
                
    def remove(self, id_or_ids: Union[UUID, str, List[Union[UUID, str]]]) -> None:
        """
        Remove programs from the local program memory.

        Parameters:
            id_or_ids (Union[UUID, str, List[Union[UUID, str]]]): A single program id or a list of program ids to be removed from the memory.
        """
        if not isinstance(id_or_ids, list):
            programs_ids = [id_or_ids]
        else:
            programs_ids = id_or_ids
        for prog_id in programs_ids:
            prog_id = str(prog_id)
            if prog_id in self._programs:
                del self._programs[prog_id]
            if prog_id in self._embeddings:
                del self._embeddings[prog_id]
            self._graph.remove_node(prog_id)
                
    def get(self, id_or_ids: Union[UUID, str, List[Union[UUID, str]]]) -> GraphProgramList:
        """
        Retrieve programs from the local program memory.

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
            if str(prog_id) in self._programs:
                prog = self._programs[str(prog_id)]
                result.progs.append(prog)
        return result
    
    def get_dependencies(self, prog_id: Union[UUID, str]) -> List[str]:
        """
        Retrieve the dependencies of a program.

        Parameters:
            prog_id (Union[UUID, str]): The id of the program whose dependencies are to be retrieved.

        Returns:
            List[str]: A list of program ids that the input program depends on.

        Raises:
            ValueError: If the program does not exist.
        """
        prog_id = str(prog_id)
        if prog_id not in self._programs:
            raise ValueError(f"GraphProgram {prog_id} does not exist.")
        return self._graph.descendants(prog_id)
    
    def depends_on(self, source_id: Union[UUID, str], target_id: Union[UUID, str]) -> bool:
        """
        Check if a program depends on another program.

        Parameters:
            source_id (Union[UUID, str]): The id of the source program.
            target_id (Union[UUID, str]): The id of the target program.

        Returns:
            List[str]: A list of program ids that form the path from the source program to the target program, if such a path exists.

        Raises:
            ValueError: If either the source program or the target program does not exist.
        """
        if source_id not in self._programs:
            raise ValueError(f"GraphProgram {source_id} does not exist.")
        if target_id not in self._programs:
            raise ValueError(f"GraphProgram {target_id} does not exist.")
        return nx.has_path(self._graph, source_id, target_id)

    def clear(self):
        """
        Clear the local document memory.
        This method removes all programs, graph, and embeddings from the memory.
        """
        self._programs = {}
        self._embeddings = {}
        self._graph = nx.DiGraph()
