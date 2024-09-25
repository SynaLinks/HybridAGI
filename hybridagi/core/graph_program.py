import dspy
import json
import re
import os
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Union
from enum import Enum
from urllib.parse import quote
from uuid import UUID, uuid4
from collections import OrderedDict
import pyjson5
import networkx as nx

def isolate(html_code: str) -> str:
    """
    When drawing the same pyvis graph from multiple cells in a jupyter notebook
    They end up sharing the same id for the javascript <script> and thus messing each other
    display(display_id=...) or making unique IDs in HTML() doesn't work unfortunately
    Here's the issue that proposes this workaround https://github.com/jupyter/notebook/issues/6598
    """
    content = quote(html_code, safe='')
    return """
    <iframe
        width="100%"
        height="610px"
        style="border: none"
        sandbox="allow-scripts allow-modals"
        referrerpolicy="no-referrer"
        src="data:text/html;charset=UTF-8,{content}"
    ></iframe>
    """.format(content=content)

class ControlType(str, Enum):
    Start = "start"
    end = "end"

class Control(BaseModel):
    id: str = Field(description="The step id")

class Action(BaseModel):
    id: str = Field(description="Unique identifier for the step")
    tool: str = Field(description="The tool name")
    purpose: str = Field(description="The action purpose")
    prompt: Optional[str] = Field(description="The prompt used to infer to tool inputs")
    var_in: Optional[List[str]] = Field(description="The list of input variables for the prompt", default=[])
    var_out: Optional[str] = Field(description="The variable to store the action output", default=None)
    disable_inference: bool = Field(description="Weither or not to disable the inference", default=False)

class Decision(BaseModel):
    id: str = Field(description="Unique identifier for the step")
    purpose: str = Field(description="The decision purpose")
    question: str = Field(description="The question to assess")
    var_in: Optional[List[str]] = Field(description="The list of input variables for the prompt", default=[])

class Program(BaseModel):
    id: str = Field(description="Unique identifier for the step")
    purpose: str = Field(description="The program call purpose")
    program: str = Field(description="The program to call")

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
    _graph = None
    
    def __init__(
            self,
            name: str,
            description: Optional[str] = None,
        ):
        BaseModel.__init__(self, name=name, description=description)
        dspy.Prediction.__init__(self, name=name, description=description)
        self._graph = nx.DiGraph()
        self.steps = OrderedDict()
        self._graph.add_node("start", label="Start", color="red")
        self._graph.add_node("end", label="End", color="red")
        self.steps["start"] = Control(id="start")
        self.steps["end"] = Control(id="end")

    def add(self, step: Union[Control | Action | Decision | Program]):
        """
        Add a step to the graph program.

        Args:
            step (Union[Control, Action, Decision, Program]): The step to add.

        Raises:
            ValueError: If the step type is invalid or if the step id already exists.
        """
        if step.id not in self.steps:
            if isinstance(step, Control):
                color = "red"
                self._graph.add_node(step.id, color=color)
            elif isinstance(step, Action):
                color = "blue"
                self._graph.add_node(step.id, title=step.prompt, color=color)
            elif isinstance(step, Decision):
                color = "green"
                self._graph.add_node(step.id, title=step.question, color=color)
            elif isinstance(step, Program):
                color = "yellow"
                self._graph.add_node(step.id, title=step.purpose, color=color)
                self.dependencies.append(step.program)
            else:
                raise ValueError(f"Invalid step type for {step.id} should be between: Control, Action, Decision, Program")
            self.steps[step.id] = step
        else:
            raise ValueError(f"Step {step.id} already exist.")

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
        if isinstance(self.steps[target], Control) and self.steps[target].id == "start":
            raise ValueError("No input edge authorized for the start Step.")
        if isinstance(self.steps[source], Action):
            if self._graph.out_degree(source) == 1:
                raise ValueError("Only one output edge is authorized for Action Steps.")
        if isinstance(self.steps[source], Control) and self.steps[source].id == "start":
            if self._graph.out_degree(source) == 1:
                raise ValueError("Only one output edge is authorized for the start Step.")
            if label != "NEXT":
                raise ValueError("Only NEXT output edge is authorized for the start Step.")
        if isinstance(self.steps[target], Control) and self.steps[target].id == "start":
            raise ValueError("No input edge is authorized for the start Step.")
        if isinstance(self.steps[source], Control) and self.steps[source].id == "end":
            raise ValueError("No output edge authorized for the end Step.")
        self._graph.add_edge(source, target, label=label)

    def get_decision_choices(self, step_id: str) -> List[str]:
        """
        Get the choices for a decision step.

        Args:
            step_ids (str): The id of the decision step.

        Returns:
            List[str]: A list of the choices for the decision step.

        Raises:
            ValueError: If the decision step does not exist or if it does not have any output edges.
        """
        if step_id not in self.steps:
            raise ValueError(f"Decision Step {step_id} does not exist.")
        if not isinstance(self.steps[step_id], Decision):
            raise ValueError(f"Step {step_id} is not a Decision.")
        return [self._graph.get_edge_data(*edge)["label"] for edge in self._graph.out_edges(step_id)]

    def build(self):
        """
        Verify the graph program.

        Raises:
            ValueError: If the graph program is not valid.
        """
        for step_id, step in self.steps.items():
            if self._graph.degree(step_id) == 0:
                raise ValueError(f"Step {step_id} is not connected to any Step.")
        for step_id, step in self.steps.items():
            if step_id != "start":
                if not self._is_reacheable("start", step_id):
                    raise ValueError(f"There is no path from the Start Step to {step_id} Step.")
            if step_id != "end":
                if not self._is_reacheable(step_id, "end"):
                    raise ValueError(f"There is no path from {step_id} Step to the End Step.")
    
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
    
    def get_next_step(self, step_id: str) -> Optional[Union[Action, Decision, Program, Control]]:
        if step_id not in self.steps:
            raise ValueError(f"Step {step_id} does not exist.")
        if isinstance(self.steps[step_id], Decision):
            raise ValueError("Cannot get the next step of a Decision")
        if len(list(self._graph.successors(step_id))) > 0:
            return self.get(list(self._graph.successors(step_id))[0])
        else:
            return None
    
    def get_decision_next_step(self, step_id: str, choice: str) -> Union[Action, Decision, Program, Control]:
        if step_id not in self.steps:
            raise ValueError(f"Step {step_id} does not exist.")
        if not isinstance(self.steps[step_id], Decision):
            raise ValueError(f"Step {step_id} is not a Decision")
        for next_step in self._graph.successors(step_id):
            if self._graph.get_edge_data(step_id, next_step)["label"] == choice:
                return self.get(next_step)
        raise ValueError(f"Next Step for {step_id} with label {choice} not found")
    
    def get_starting_step(self):
        return self.get_next_step("start")
                
    def get(self, step_id: str) -> Union[Action, Decision, Program, Control]:
        if step_id not in self.steps:
            raise ValueError(f"Step {step_id} does not exist.")
        return self.steps[step_id]
    
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
                step_id, step_type, step_props = step
                step_id = step_id.strip()
                step_type = step_type.strip()
                step_props = '{' + step_props.strip() + '}'
                step_props = pyjson5.loads(step_props)
                if step_type == "Control":
                    self.add(Control(id=step_props["id"]))
                elif step_type == "Action":
                    if "id" not in step_props:
                        raise ValueError(f"{step_id} Action node should have \"{step_id}\" in its id field")
                    if "purpose" not in step_props:
                        raise ValueError(f"{step_id} Action node should have a purpose field")
                    if "tool" not in step_props:
                        raise ValueError(f"{step_id} Action node should have a tool field")
                    if "prompt" not in step_props:
                        raise ValueError(f"{step_id} Action node should have a prompt field")
                    self.add(Action(
                        id=step_props["id"],
                        purpose=step_props["purpose"],
                        tool=step_props["tool"],
                        prompt=step_props["prompt"],
                        var_in=step_props["var_in"] if "var_in" in step_props else [],
                        var_out=step_props["var_out"] if "var_out" in step_props else None,
                        disable_inference=True if "disable_inference" in step_props else False,
                    ))
                elif step_type == "Decision":
                    if "id" not in step_props:
                        raise ValueError(f"{step_id} Decision node should have \"{step_id}\" in its id field")
                    if "purpose" not in step_props:
                        raise ValueError(f"{step_id} Decision node should have a purpose field")
                    if "question" not in step_props:
                        raise ValueError(f"{step_id} Decision node should have a question field")
                    self.add(Decision(
                        id=step_props["id"],
                        purpose=step_props["purpose"],
                        question=step_props["question"],
                        var_in=step_props["var_in"] if "var_in" in step_props else [],
                    ))
                elif step_type == "Program":
                    if "id" not in step_props:
                        raise ValueError(f"{step_id} Program node should have \"{step_id}\" in its id field")
                    if "purpose" not in step_props:
                        raise ValueError(f"{step_id} Program node should have a purpose field")
                    if "program" not in step_props:
                        raise ValueError(f"{step_id} Program node should have a program field")
                    self.add(Program(
                        id=step_props["id"],
                        purpose=step_props["purpose"],
                        program=step_props["program"],
                    ))
                else:
                    raise ValueError(f"Invalid step type for {step_id} should be between: Control, Action, Decision, Program")
            # Parse relations
            relations = re.findall(r'\((.*?)\)-(\[.*?\])\s*->\s*\((.*?)\)', cleaned_query)
            for relation in relations:
                source_name, label, target_name = relation
                label = label.strip("[:]")
                self.connect(source_name, target_name, label=label)
            return self
        raise ValueError("Invalid format, no CREATE command detected")
    
    def __str__(self):
        return self.to_cypher()
        
    def to_cypher(self):
        """
        Convert the graph program to a Cypher query.

        Returns:
            str: The Cypher query representing the graph program.
        """
        cypher = f"// @desc: {self.description}\nCREATE\n// Nodes declaration"
        key_quotes_regex = r"\"([^\"]+)\":"
        sub_regex = r"\1:"
        for step_id, step in self.steps.items():
            if isinstance(step, Control):
                args = {
                    "id": step.id.value if isinstance(step.id, ControlType) else step.id,
                }
                cleaned_args = re.sub(key_quotes_regex, sub_regex, json.dumps(args))
                cypher += f"\n({step_id}:Control "+cleaned_args+"),"
            elif isinstance(step, Action):
                args = {
                    "id": step_id,
                    "purpose": step.purpose,
                    "tool": step.tool,
                }
                if step.prompt:
                    args["prompt"] = step.prompt
                if step.var_in and len(step.var_in) > 0:
                    args["var_in"] = step.var_in
                if step.var_out:
                    args["var_out"] = step.var_out
                if step.disable_inference is True:
                    args["disable_inference"] = True
                cleaned_args = re.sub(key_quotes_regex, sub_regex, json.dumps(args, indent=2))
                cypher += f"\n({step_id}:Action "+cleaned_args+"),"
            elif isinstance(step, Decision):
                args = {
                    "id": step_id,
                    "purpose": step.purpose,
                    "question": step.question,
                }
                if len(step.var_in) > 0:
                    args["var_in"] = step.var_in
                cleaned_args = re.sub(key_quotes_regex, sub_regex, json.dumps(args, indent=2))
                cypher += f"\n({step_id}:Decision "+cleaned_args+"),"
            elif isinstance(step, Program):
                args = {
                    "id": step_id,
                    "purpose": step.purpose,
                    "program": step.program,
                }
                cleaned_args = re.sub(key_quotes_regex, sub_regex, json.dumps(args, indent=2))
                cypher += f"\n({step_id}:Program "+cleaned_args+"),"
        cypher += "\n// Structure declaration"
        for step_id, step in self.steps.items():
            for edge in self._graph.edges(step_id):
                source_name, target_name = edge
                label = self._graph.get_edge_data(source_name, target_name)["label"]
                cypher += f"\n({source_name})-[:"+label+f"]->({target_name}),"
        cypher = cypher.rstrip(",")
        return cypher
    
    def to_dict(self):
        return {"name": self.name, "routine": self.to_cypher()}
    
    def save(self, folderpath: str = ""):
        """
        Save the graph program as a Cypher file
        
        Parameters:
            filepath (str): The path of the file (default empty) if empty, save it into '{self.name}.cypher' file.         
        """
        filename = f"{self.name}.cypher"
        if folderpath == "":
            filepath = filename
        else:
            filepath = os.path.join(folderpath, filename)
        with open(filepath, 'w') as f:
            f.write(self.to_cypher())
    
    def show(self, notebook: bool = False, cdn_resources: str = 'in_line') -> None:
        """
        Visualize the local memory as a network graph.

        Parameters:
            notebook (bool): Whether to display the graph in a Jupyter notebook or not.
            cdn_resources (str): Where to pull resources for css and js files. Defaults to local.
                Options ['local','in_line','remote'].
                local: pull resources from local lib folder.
                in_line: insert lib resources as inline script tags.
                remote: pull resources from hash checked cdns.
        """
        from pyvis.network import Network
        net = Network(notebook=notebook, directed=True, cdn_resources=cdn_resources)
        net.from_nx(self._graph)
        net.toggle_physics(True)

        if notebook:
            from IPython.display import display, HTML
            unique_id = f'{uuid4().hex}.html'
            html = net.generate_html(unique_id, notebook=True)
            display(HTML(isolate(html)), display_id=unique_id)
        else:
            net.show(f'{self.name}.html', notebook=notebook)