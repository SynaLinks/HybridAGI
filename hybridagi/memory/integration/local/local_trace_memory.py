from typing import Union, List, Dict, Optional
from uuid import UUID
from collections import OrderedDict
from hybridagi.memory.trace_memory import TraceMemory
from hybridagi.core.datatypes import AgentStep, AgentStepList, AgentStepType
import networkx as nx

from .local_memory import LocalMemory

class LocalTraceMemory(LocalMemory, TraceMemory):
    """
    A class used to manage and store agent steps locally.

    Attributes:
        index_name (str): The name of the index used for trace storage.
        wipe_on_start (bool): Whether to clear the memory when the object is initialized.
        _steps (Optional[Dict[str, AgentStep]]): A dictionary to store agent steps. The keys are step IDs and the values are AgentStep objects.
        _embeddings (Optional[Dict[str, List[float]]]): An ordered dictionary to store step embeddings. The keys are step IDs and the values are lists of floats representing the embeddings.
        _graph (nx.DiGraph): A directed graph to store the relationships between steps.
    """
    index_name: str
    wipe_on_start: bool
    _steps: Optional[Dict[str, AgentStep]] = {}
    _embeddings: Optional[Dict[str, List[float]]] = OrderedDict()
    _graph: nx.DiGraph()
    
    def __init__(
            self,
            index_name: str,
            wipe_on_start: bool = True,
        ):
        """
        Initialize the local trace memory.

        Parameters:
            index_name (str): The name of the index used for trace storage.
            wipe_on_start (bool): Whether to clear the memory when the object is initialized.
        """
        self.index_name = index_name
        self.wipe_on_start = wipe_on_start
        if wipe_on_start:
            self.clear()
            
    def exist(self, step_id: Union[UUID, str]) -> bool:
        return step_id in self._steps
    
    def update(self, step_or_steps: Union[AgentStep, AgentStepList]) -> None:
        """
        Update the local trace memory with new agent steps.

        Parameters:
            step_or_steps (Union[AgentStep, AgentStepList]): A single step or a list of steps to be added to the memory.

        Raises:
            ValueError: If the input is not an AgentStep or AgentStepList.
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
            if step.step_type == AgentStepType.Action:
                color = "blue"
            elif step.step_type == AgentStepType.Decision:
                color = "green"
            else:
                color = "orange"
            if step_id not in self._steps:
                parent_id = str(step.parent_id)
                if step.parent_id is not None:
                    parent_id = str(step.parent_id)
                    self._graph.add_node(step_id, color=color, title=str(step))
                    if parent_id in self._steps:
                        self._graph.add_edge(parent_id, step_id, label="NEXT")
                else:
                    self._graph.add_node(step_id, color=color, title=str(step))
            self._steps[step_id] = step
            if step.vector is not None:
                self._embeddings[step_id] = step.vector

    def get(self, id_or_ids: Union[UUID, str, List[Union[UUID, str]]]) -> AgentStepList:
        """
        Retrieve agent steps from the local trace memory.

        Parameters:
            id_or_ids (Union[UUID, str, List[Union[UUID, str]]]): A single step ID or a list of step IDs to be retrieved from the memory.

        Returns:
            AgentStepList: A list of steps that match the input IDs.
        """
        if not isinstance(id_or_ids, list):
            steps_ids = [id_or_ids]
        else:
            steps_ids = id_or_ids
        result = AgentStepList()
        for step_id in steps_ids:
            if str(step_id) in self._steps:
                step = self._steps[str(step_id)]
                result.steps.append(step)
        return result
        
    def clear(self):
        """
        Clear the local document memory.
        This method removes all steps, graph, and embeddings from the memory.
        """
        self._steps = {}
        self._embeddings = OrderedDict()
        self._graph = nx.DiGraph()
