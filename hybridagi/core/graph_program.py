import dspy
import json
import re
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Union
from enum import Enum
from uuid import UUID, uuid4
import pyjson5

### Program memory related types

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
    program_name: str = Field(description="The program to call")
    prompt: str = Field(description="The prompt to give as input to the called program")
    inputs: Optional[List[str]] = Field(description="The prompt var inputs", default=[])
    output: Optional[str] = Field(description="", default=None)

class GraphProgram(BaseModel, dspy.Prediction):
    """
    A class representing a graph program.

    Attributes:
        name (Optional[str]): A unique identifier for the graph program.
        description (Optional[str]): A natural language description of the graph program.
        vector (Optional[List[float]]): A vector representation of the graph program.
        metadata (Optional[Dict[str, Any]]): Additional information about the graph program.
        _nodes (Optional[Dict[str, Optional[Union[Control, Action, Decision, Program]]]]): A dictionary of nodes in the graph program.
        _edges (Optional[Dict[str, Dict[str, str]]]): A dictionary of edges in the graph program.
        _edges_count (Optional[Dict[str, int]]): A dictionary of the number of edges connected to each node in the graph program.
    """
    name: Optional[str] = Field(description="Unique identifier for the cypher program", default=None)
    description: Optional[str] = Field(description="The natural language description of the cypher program", default=None)
    vector: Optional[List[float]] = Field(description="Vector representation of the cypher program", default=None)
    metadata: Optional[Dict[str, Any]] = Field(description="Additional information about the cypher program", default={})
    _nodes: Optional[Dict[str, Optional[Union[Control, Action, Decision, Program]]]] = \
    {
        "start": Control(purpose="Start"),
        "end": Control(purpose="End"),
    }
    _edges: Optional[Dict[str, Dict[str, str]]] = {}
    _edges_count: Optional[Dict[str, int]] = {}
    _dependencies: Optional[List[str]] = []

    def add(self, node_name: str, node: Union[Control | Action | Decision | Program]):
        """
        Add a node to the graph program.

        Args:
            node_name (str): The name of the node to add.
            node (Union[Control, Action, Decision, Program]): The node to add.

        Raises:
            ValueError: If the node type is invalid or if the node name already exists.
        """    
        if not isinstance(node, Control) and \
            not isinstance(node, Action) and \
                not isinstance(node, Decision) and \
                    not isinstance(node, Program):
            raise ValueError(f"Invalid node type for {node_name} should be between: Control, Action, Decision, Program")
        if node_name not in self._nodes:
            self._nodes[node_name] = node
        else:
            raise ValueError(f"Node {node_name} already exist.")
        if isinstance(node, Program):
            self._dependencies.append(node_name)

    def connect(self, source: str, target: str, label: str = "NEXT"):
        """
        Connect two nodes in the graph program.

        Args:
            source (str): The name of the source node.
            target (str): The name of the target node.
            label (str, optional): The label for the edge between the source and target nodes. Defaults to "NEXT".

        Raises:
            ValueError: If the source or target node does not exist, if the edge type is invalid, or if the edge already exists.
        """
        label = label.upper()
        if source not in self._nodes:
            raise ValueError(f"Node {source} does not exist.")
        if target not in self._nodes:
            raise ValueError(f"Node {target} does not exist.")
        if isinstance(self._nodes[source], Action) and isinstance(self._nodes[target], Action):
            if label != "NEXT":
                raise ValueError("Only NEXT edge is authorized between two Action Nodes.")
        if isinstance(self._nodes[source], Action) and isinstance(self._nodes[target], Program):
            if label != "NEXT":
                raise ValueError("Only NEXT edge is authorized between Action and Program Nodes.")
        if isinstance(self._nodes[source], Action) and isinstance(self._nodes[target], Decision):
            if label != "NEXT":
                raise ValueError("Only NEXT edge is authorized between Action and Decision Nodes.")
        if isinstance(self._nodes[target], Control) and self._nodes[target].purpose == "Start":
            raise ValueError("No input edge authorized for the Start Node.")
        if isinstance(self._nodes[source], Action):
            if source in self._edges:
                if len(self._edges[source]) > 1:
                    raise ValueError("Only one output edge is authorized for Action Nodes.")
        if isinstance(self._nodes[source], Control) and self._nodes[source].purpose == "Start":
            if source in self._edges:
                if len(self._edges[source]) > 1:
                    raise ValueError("Only one output edge is authorized for the Start Node.")
                if label != "NEXT":
                    raise ValueError("Only NEXT output edge is authorized for the Start Node.")
        if isinstance(self._nodes[target], Control) and self._nodes[target].purpose == "Start":
            raise ValueError("No input edge is authorized for the Start Node.")
        if isinstance(self._nodes[source], Control) and self._nodes[source].purpose == "End":
            raise ValueError("No output edge authorized for the end Node.")
        if source not in self._edges:
            self._edges[source] = {}
        if source not in self._edges_count:
            self._edges_count[source] = 0
        self._edges_count[source] += 1
        if target not in self._edges_count:
            self._edges_count[target] = 0
        self._edges_count[target] += 1
        self._edges[source][target] = label

    def get_decision_choices(self, decision_name: str) -> List[str]:
        """
        Get the choices for a decision node.

        Args:
            decision_name (str): The name of the decision node.

        Returns:
            List[str]: A list of the choices for the decision node.

        Raises:
            ValueError: If the decision node does not exist or if it does not have any output edges.
        """
        if decision_name not in self._nodes:
            raise ValueError(f"Decision Node {decision_name} does not exist.")
        if not isinstance(self._nodes[decision_name], Decision):
            raise ValueError(f"Node {decision_name} is not a Decision.")
        if decision_name not in self._edges:
            raise ValueError(f"No output edge for {decision_name} Decision")
        return [label for label in self._edges[decision_name].values()]

    def get_dependencies(self) -> List[str]:
        """
        Get the local dependencies of the graph program.

        Returns:
            List[str]: A list of the local dependencies of the graph program.
        """
        return self._dependencies

    def build(self):
        """
        Verify the graph program.

        Raises:
            ValueError: If the graph program is not valid.
        """
        for node_name, node in self._nodes.items():
            if node_name in self._edges_count:
                if self._edges_count[node_name] == 0:
                    raise ValueError(f"Node {node_name} is not connected to any Node.")
            else:
                raise ValueError(f"Node {node_name} is not connected to any Node.")
        for node_name, node in self._nodes.items():
            if node_name != "start":
                if not self._is_connected("start", node_name):
                    raise ValueError(f"There is no path from the Start Node to {node_name} Node.")
            if node_name != "end":
                if not self._is_connected(node_name, "end"):
                    raise ValueError(f"There is no path from {node_name} Node to the End Node.")
    
    def _is_connected(self, start_node: str, end_node: str) -> bool:
        """
        Check if the start node is connected to the end node.

        Args:
            start_node (str): The name of the start node.
            end_node (str): The name of the end node.

        Returns:
            bool: True if the start node is connected to the end node, False otherwise.

        Raises:
            ValueError: If the start or end node does not exist.
        """
        if start_node not in self._nodes:
            raise ValueError(f"Node {start_node} does not exist.")
        if end_node not in self._nodes:
            raise ValueError(f"Node {end_node} does not exist.")

        visited = set()

        def dfs(node):
            if node == end_node:
                return True
            visited.add(node)
            if node in self._edges:
                for neighbor in self._edges[node]:
                    if neighbor not in visited:
                        if dfs(neighbor):
                            return True
            return False

        return dfs(start_node)
    
    def clear(self):
        """
        Clear the graph program.
        """
        self._nodes = {}
        self._edges = {}
        self._edges_count = {}
        self._dependencies = []
        
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
        self.clear()
        description = re.search(r'// @desc:(.*)', cypher_query)
        if description:
            self.description = description.group().replace("// @desc:","").strip()
        else:
            raise ValueError("You should provide a description using `// @desc:`")
        create_command = re.search(r'CREATE(.*)', cypher_query, re.DOTALL)
        if create_command:
            # Remove comments
            cleaned_query = re.sub(r'//.*?\n', '', create_command.group(1))
            # Parse nodes
            print(cleaned_query)
            nodes = re.findall(r'\(([^:]+):([^ ]+)\s*\{(.*?)\}\)', cleaned_query, re.DOTALL)
            for node in nodes:
                node_name, node_type, node_props = node
                node_name = node_name.strip()
                node_type = node_type.strip()
                # print(node_name, node_type, node_props)
                node_props = '{' + node_props.strip() + '}'
                node_props = pyjson5.loads(node_props)
                if node_type == "Control":
                    self.add(node_name, Control(purpose=node_props["purpose"]))
                elif node_type == "Action":
                    self.add(node_name, Action(
                        purpose=node_props["purpose"],
                        tool=node_props["tool"],
                        prompt=node_props["prompt"],
                        inputs=node_props["inputs"] if "inputs" in node_props else None,
                        output=node_props["output"] if "output" in node_props else None,
                    ))
                elif node_type == "Decision":
                    self.add(node_name, Decision(
                        purpose=node_props["purpose"],
                        prompt=node_props["prompt"],
                        inputs=node_props["inputs"] if "inputs" in node_props else None,
                    ))
                elif node_type == "Program":
                    self.add(node_name, Decision(
                        purpose=node_props["purpose"],
                        prompt=node_props["prompt"],
                        inputs=node_props["inputs"] if "inputs" in node_props else None,
                        output=node_props["output"] if "output" in node_props else None,
                    ))
                else:
                    raise ValueError(f"Invalid node type for {node_name} should be between: Control, Action, Decision, Program")
            # Parse relations
            relations = re.findall(r'\((.*?)\)-(\[.*?\])\s*->\s*\((.*?)\)', cleaned_query)
            for relation in relations:
                source_name, label, target_name = relation
                label = label.strip("[:]")
                print(source_name, label, target_name)
                self.connect(source_name, target_name, label=label)
            self.build()
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
        for node_name, node in self._nodes.items():
            if isinstance(node, Control):
                args = {
                    "purpose": node.purpose,
                }
                cleaned_args = re.sub(key_quotes_regex, sub_regex, json.dumps(args))
                cypher += f"\n({node_name}:Control "+cleaned_args+"),"
            elif isinstance(node, Action):
                args = {
                    "purpose": node.purpose,
                    "tool": node.tool,
                }
                if node.prompt:
                    args["prompt"] = node.prompt
                if len(node.inputs) > 0:
                    args["inputs"] = node.inputs
                if node.output:
                    args["output"] = node.output
                cleaned_args = re.sub(key_quotes_regex, sub_regex, json.dumps(args, indent=2))
                cypher += f"\n({node_name}:Action "+cleaned_args+"),"
            elif isinstance(node, Decision):
                args = {
                    "purpose": node_name,
                    "prompt": node.prompt,
                }
                if len(node.inputs) > 0:
                    args["inputs"] = node.inputs
                cleaned_args = re.sub(key_quotes_regex, sub_regex, json.dumps(args, indent=2))
                cypher += f"\n({node_name}:Decision "+cleaned_args+"),"
            elif isinstance(node, Program):
                args = {
                    "purpose": node.purpose,
                    "program": node.program,
                    "prompt": node.prompt
                }
                if len(node.inputs) > 0:
                    args["inputs"] = node.inputs
                if node.output:
                    args["output"] = node.output
                cleaned_args = re.sub(key_quotes_regex, sub_regex, json.dumps(args, indent=2))
                cypher += f"\n({node_name}:Program "+cleaned_args+"),"
        cypher += "\n// Structure declaration"
        for source_name in self._edges.keys():
            for target_name in self._edges[source_name].keys():
                label = self._edges[source_name][target_name]
                cypher += f"\n({source_name})-[:"+label+f"]->({target_name}),"
        cypher = cypher.rstrip(",")
        return cypher
    
    def visualize(self, notebook: bool=False):
        """
        Visualize the graph program as a network graph.

        Parameters:
            notebook (bool): Whether to display the graph in a Jupyter notebook or not.
        """
        from pyvis.network import Network
        net = Network(notebook=notebook, directed=True)
        for node_name, node in self._nodes.items():
            if isinstance(node, Control):
                color = "red"
            elif isinstance(node, Action):
                color = "blue"
            if isinstance(node, Decision):
                color = "green"
            elif isinstance(node, Program):
                color = "yellow"
            net.add_node(node_name, label=node.purpose, color=color)
        for source_id in self._edges:
            for target_id in self._edges[source_id]:
                if len(self._edges[source_id][target_id]) > 0:
                    net.add_edge(source_id, target_id)
        net.toggle_physics(True)
        net.show(f'{self.name}.html', notebook=notebook)
    
class GraphProgramList(BaseModel):
    programs: Optional[List[GraphProgram]] = Field(description="List of graph programs", default=[])