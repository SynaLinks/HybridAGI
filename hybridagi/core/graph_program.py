import dspy
import json
import re
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Union
from enum import Enum
from uuid import UUID, uuid4
from collections import OrderedDict
import pyjson5
import networkx as nx

class ControlType(str, Enum):
    Start = "Start"
    end = "End"

class Control(BaseModel):
    purpose: ControlType

class Action(BaseModel):
    purpose: str
    tool: str
    prompt: Optional[str] = None
    inputs: Optional[List[str]] = []
    output: Optional[str] = None

class Decision(BaseModel):
    purpose: str = Field(description="The purpose of the decision-making step")
    prompt: str = Field(description="The prompt to make the decision")
    inputs: Optional[List[str]] = Field(description="The prompt var inputs", default=[])

class Program(BaseModel):
    purpose: str = Field(description="The purpose of the program call")
    program: str = Field(description="The program to call")
    prompt: str = Field(description="The prompt to give as input to the called program")
    inputs: Optional[List[str]] = Field(description="The prompt var inputs", default=[])
    output: Optional[str] = Field(description="", default=None)

class GraphProgram(BaseModel, dspy.Prediction):
    """
    A class representing a graph program.
    """
    name: Optional[str] = Field(description="Unique identifier for the cypher program")
    description: Optional[str] = Field(description="The natural language description of the cypher program", default=None)
    vector: Optional[List[float]] = Field(description="Vector representation of the cypher program", default=None)
    metadata: Optional[Dict[str, Any]] = Field(description="Additional information about the cypher program", default={})
    steps: Optional[Dict[str, Optional[Union[Control, Action, Decision, Program]]]] = Field(description="Steps of the cypher program", default={})
    dependencies: Optional[List[str]] = Field(description="Dependencies of the cypher program", default=[])
    _graph = nx.DiGraph()
    
    def __init__(
            self,
            name: str,
            description: Optional[str] = None,
        ):
        super().__init__(name=name, description=description)
        self._graph.add_node("start", label="Start", color="red")
        self._graph.add_node("end", label="End", color="red")
        self.steps = OrderedDict()
        self.steps["start"] = Control(purpose="Start")
        self.steps["end"] = Control(purpose="End")

    def add(self, step_name: str, step: Union[Control | Action | Decision | Program]):
        """
        Add a step to the graph program.

        Args:
            step_name (str): The name of the step to add.
            step (Union[Control, Action, Decision, Program]): The step to add.

        Raises:
            ValueError: If the step type is invalid or if the step name already exists.
        """
        if step_name not in self.steps:
            if isinstance(step, Control):
                color = "red"
                self._graph.add_node(step_name, label=step.purpose, color=color)
            elif isinstance(step, Action):
                color = "blue"
                self._graph.add_node(step_name, label=step.purpose, title=step.prompt, color=color)
            elif isinstance(step, Decision):
                color = "green"
                self._graph.add_node(step_name, label=step.purpose, title=step.prompt, color=color)
            elif isinstance(step, Program):
                color = "yellow"
                self._graph.add_node(step_name, label=step.purpose, title=step.prompt, color=color)
                self.dependencies.append(step_name)
            else:
                raise ValueError(f"Invalid step type for {step_name} should be between: Control, Action, Decision, Program")
            self.steps[step_name] = step
        else:
            raise ValueError(f"Step {step_name} already exist.")

    def connect(self, source: str, target: str, label: str = "NEXT"):
        """
        Connect two steps in the graph program.

        Args:
            source (str): The name of the source step.
            target (str): The name of the target step.
            label (str, optional): The label for the edge between the source and target steps. Defaults to "NEXT".

        Raises:
            ValueError: If the source or target step does not exist, if the edge type is invalid, or if the edge already exists.
        """
        label = label.upper().replace(" ", "_")
        if source not in self.steps:
            raise ValueError(f"Step {source} does not exist.")
        if target not in self.steps:
            raise ValueError(f"Step {target} does not exist.")
        if isinstance(self.steps[source], Action) and isinstance(self.steps[target], Action):
            if label != "NEXT":
                raise ValueError("Only NEXT edge is authorized between two Action Steps.")
        if isinstance(self.steps[source], Action) and isinstance(self.steps[target], Program):
            if label != "NEXT":
                raise ValueError("Only NEXT edge is authorized between Action and Program Steps.")
        if isinstance(self.steps[source], Action) and isinstance(self.steps[target], Decision):
            if label != "NEXT":
                raise ValueError("Only NEXT edge is authorized between Action and Decision Steps.")
        if isinstance(self.steps[target], Control) and self.steps[target].purpose == "Start":
            raise ValueError("No input edge authorized for the start Step.")
        if isinstance(self.steps[source], Action):
            if self._graph.out_degree(source) == 1:
                raise ValueError("Only one output edge is authorized for Action Steps.")
        if isinstance(self.steps[source], Control) and self.steps[source].purpose == "Start":
            if self._graph.out_degree(source) == 1:
                raise ValueError("Only one output edge is authorized for the start Step.")
            if label != "NEXT":
                raise ValueError("Only NEXT output edge is authorized for the start Step.")
        if isinstance(self.steps[target], Control) and self.steps[target].purpose == "Start":
            raise ValueError("No input edge is authorized for the start Step.")
        if isinstance(self.steps[source], Control) and self.steps[source].purpose == "End":
            raise ValueError("No output edge authorized for the end Step.")
        self._graph.add_edge(source, target, label=label)

    def get_decision_choices(self, step_name: str) -> List[str]:
        """
        Get the choices for a decision step.

        Args:
            step_name (str): The name of the decision step.

        Returns:
            List[str]: A list of the choices for the decision step.

        Raises:
            ValueError: If the decision step does not exist or if it does not have any output edges.
        """
        if step_name not in self.steps:
            raise ValueError(f"Decision Step {step_name} does not exist.")
        if not isinstance(self.steps[step_name], Decision):
            raise ValueError(f"Step {step_name} is not a Decision.")
        return [self._graph.get_edge_data(*edge)["label"] for edge in self._graph.out_edges(step_name)]

    def build(self):
        """
        Verify the graph program.

        Raises:
            ValueError: If the graph program is not valid.
        """
        for step_name, step in self.steps.items():
            if self._graph.degree(step_name) == 0:
                raise ValueError(f"Step {step_name} is not connected to any Step.")
        for step_name, step in self.steps.items():
            if step_name != "start":
                if not self._is_reacheable("start", step_name):
                    raise ValueError(f"There is no path from the Start Step to {step_name} Step.")
            if step_name != "end":
                if not self._is_reacheable(step_name, "end"):
                    raise ValueError(f"There is no path from {step_name} Step to the End Step.")
    
    def _is_reacheable(self, source_step: str, target_step: str) -> bool:
        """
        Check if the source step is connected to the target step.

        Args:
            source_step (str): The name of the source step.
            target_step (str): The name of the target step.

        Returns:
            bool: True if the start step is connected to the end step, False otherwise.

        Raises:
            ValueError: If the start or end step does not exist.
        """
        if source_step not in self.steps:
            raise ValueError(f"Step {source_step} does not exist.")
        if target_step not in self.steps:
            raise ValueError(f"Step {target_step} does not exist.")
        return nx.has_path(self._graph, source_step, target_step)
    
    def clear(self):
        """
        Clear the graph program.
        """
        self.steps = {}
        self._graph = nx.DiGraph()
        self.dependencies = []
        
    def from_cypher(self, cypher_query: str) -> Optional["GraphProgram"]:
        """
        Parse a Cypher query and create a graph program from it.

        Args:
            cypher_query (str): The Cypher query to parse.

        Returns:
            Optional[GraphProgram]: The graph program created from the Cypher query, or None if the query is invalid.

        Raises:
            ValueError: If the Cypher query is invalid.
        """
        # Get description
        description = re.search(r'// @desc:(.*)', cypher_query)
        if description:
            self.description = description.group().replace("// @desc:","").strip()
        else:
            raise ValueError("You should provide a description using `// @desc:`")
        create_command = re.search(r'CREATE(.*)', cypher_query, re.DOTALL)
        if create_command:
            self.clear()
            # Remove comments
            cleaned_query = re.sub(r'//.*?\n', '', create_command.group(1))
            # Parse steps
            steps = re.findall(r'\(([^:]+):([^ ]+)\s*\{(.*?)\}\)', cleaned_query, re.DOTALL)
            for step in steps:
                step_name, step_type, step_props = step
                step_name = step_name.strip()
                step_type = step_type.strip()
                step_props = '{' + step_props.strip() + '}'
                step_props = pyjson5.loads(step_props)
                if step_type == "Control":
                    self.add(step_name, Control(purpose=step_props["purpose"]))
                elif step_type == "Action":
                    self.add(step_name, Action(
                        purpose=step_props["purpose"],
                        tool=step_props["tool"],
                        prompt=step_props["prompt"],
                        inputs=step_props["inputs"] if "inputs" in step_props else None,
                        output=step_props["output"] if "output" in step_props else None,
                    ))
                elif step_type == "Decision":
                    self.add(step_name, Decision(
                        purpose=step_props["purpose"],
                        prompt=step_props["prompt"],
                        inputs=step_props["inputs"] if "inputs" in step_props else None,
                    ))
                elif step_type == "Program":
                    self.add(step_name, Decision(
                        purpose=step_props["purpose"],
                        prompt=step_props["prompt"],
                        inputs=step_props["inputs"] if "inputs" in step_props else None,
                        output=step_props["output"] if "output" in step_props else None,
                    ))
                else:
                    raise ValueError(f"Invalid step type for {step_name} should be between: Control, Action, Decision, Program")
            # Parse relations
            relations = re.findall(r'\((.*?)\)-(\[.*?\])\s*->\s*\((.*?)\)', cleaned_query)
            for relation in relations:
                source_name, label, target_name = relation
                label = label.strip("[:]")
                self.connect(source_name, target_name, label=label)
            return self
        raise ValueError("Invalid format, no CREATE command detected")
        
    def to_cypher(self):
        """
        Convert the graph program to a Cypher query.

        Returns:
            str: The Cypher query representing the graph program.
        """
        cypher = f"// @desc: {self.description}\nCREATE\n// Nodes declaration"
        key_quotes_regex = r"\"([^\"]+)\":"
        sub_regex = r"\1:"
        for step_name, step in self.steps.items():
            if isinstance(step, Control):
                args = {
                    "purpose": step.purpose,
                }
                cleaned_args = re.sub(key_quotes_regex, sub_regex, json.dumps(args))
                cypher += f"\n({step_name}:Control "+cleaned_args+"),"
            elif isinstance(step, Action):
                args = {
                    "purpose": step.purpose,
                    "tool": step.tool,
                }
                if step.prompt:
                    args["prompt"] = step.prompt
                if len(step.inputs) > 0:
                    args["inputs"] = step.inputs
                if step.output:
                    args["output"] = step.output
                cleaned_args = re.sub(key_quotes_regex, sub_regex, json.dumps(args, indent=2))
                cypher += f"\n({step_name}:Action "+cleaned_args+"),"
            elif isinstance(step, Decision):
                args = {
                    "purpose": step.purpose,
                    "prompt": step.prompt,
                }
                if len(step.inputs) > 0:
                    args["inputs"] = step.inputs
                cleaned_args = re.sub(key_quotes_regex, sub_regex, json.dumps(args, indent=2))
                cypher += f"\n({step_name}:Decision "+cleaned_args+"),"
            elif isinstance(step, Program):
                args = {
                    "purpose": step.purpose,
                    "program": step.program,
                    "prompt": step.prompt
                }
                if len(step.inputs) > 0:
                    args["inputs"] = step.inputs
                if step.output:
                    args["output"] = step.output
                cleaned_args = re.sub(key_quotes_regex, sub_regex, json.dumps(args, indent=2))
                cypher += f"\n({step_name}:Program "+cleaned_args+"),"
        cypher += "\n// Structure declaration"
        for step_name, step in self.steps.items():
            for edge in self._graph.edges(step_name):
                source_name, target_name = edge
                label = self._graph.get_edge_data(source_name, target_name)["label"]
                cypher += f"\n({source_name})-[:"+label+f"]->({target_name}),"
        cypher = cypher.rstrip(",")
        return cypher
    
    def show(self, notebook: bool=False):
        """
        Visualize the graph program as a network graph.

        Parameters:
            notebook (bool): Whether to display the graph in a Jupyter notebook or not.
        """
        from pyvis.network import Network
        net = Network(notebook=notebook, directed=True)
        net.from_nx(self._graph)
        net.toggle_physics(True)
        net.show(f'{self.name}.html', notebook=notebook)
    
class GraphProgramList(BaseModel):
    progs: Optional[List[GraphProgram]] = Field(description="List of graph programs", default=[])