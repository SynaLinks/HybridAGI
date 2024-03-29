import dspy
import copy
from falkordb import Node, Graph
from typing import List, Optional, Union
from collections import deque
from ..hybridstores.program_memory.program_memory import ProgramMemory
from ..types.actions import AgentAction, AgentDecision, ProgramCall, ProgramEnd

class DecisionSignature(dspy.Signature):
    """Answer the assessed question without additional details"""
    trace = dspy.InputField(desc="The previous actions")
    purpose = dspy.InputField(desc="The purpose of the question")
    question = dspy.InputField(desc="The question to assess")
    options = dspy.InputField(desc="The possible answers to the assessed question")
    answer = dspy.OutputField(desc=f"Answer to the assessed question (only ONE word) without additional details")

class FinishSignature(dspy.Signature):
    """Generate the final answer if the objective is a question or a summary of the previous actions otherwise"""
    trace = dspy.InputField(desc="Previous actions")
    objective = dspy.InputField(desc="Long-term objective")
    answer = dspy.OutputField(desc="Final answer if the objective is a question or a summary of the previous actions otherwise")

class GraphProgramInterpreter(dspy.Module):
    """The graph program interpreter (aka the reasoning module of HybridAGI)"""
    
    def __init__(
            self,
            program_memory: ProgramMemory,
            tools: List[dspy.BaseModule] = [],
            objective: str = "N/A",
            entrypoint: str = "main",
            num_history: int = 5,
            max_iters: int = 20,
            commit_decision: bool = True,
            commit_program_flow: bool = True,
            stop: Optional[str] = None,
        ):
        self.program_memory = program_memory
        self.objective = objective
        self.entrypoint = entrypoint
        self.num_history = num_history
        self.max_iters = max_iters
        self.commit_decision = commit_decision
        self.commit_program_flow = commit_program_flow
        self.program_stack = deque()
        self.program_trace = []
        self.current_hop = 0
        self.program_memory = program_memory
        self.stop = stop
        # DSPy reasoners
        self.tools = {tool.name: tool for tool in tools}
        self.decision = dspy.TypedChainOfThought(DecisionSignature)
        self.finish = dspy.ChainOfThought(FinishSignature)
        super().__init__()

    def run_step(self) -> Union[AgentAction, AgentDecision, ProgramCall, ProgramEnd]:
        """Method to run a step of the program"""
        current_node = self.get_current_node()
        if current_node:
            self.current_hop += 1
            if current_node.labels[0] == "Program":
                try:
                    program_purpose = current_node.properties["name"]
                    program_name = current_node.properties["program"]
                except ValueError:
                    raise RuntimeError("Program node invalid: missing a required parameter")
                step = self.call_program(program_purpose, program_name)
                if self.commit_program_flow:
                    self.program_trace.append(str(step))
            elif current_node.labels[0] == "Action":
                try:
                    action_purpose = current_node.properties["name"]
                    action_tool = current_node.properties["tool"]
                    if "prompt" in current_node.properties:
                        action_prompt = current_node.properties["prompt"]
                    else:
                        action_prompt = ""
                    if "disable_inference" in current_node.properties:
                        disable_inference = current_node.properties["disable_inference"].lower == "true"
                    else:
                        disable_inference = False
                except ValueError:
                    raise RuntimeError("Action node invalid: missing a required parameter")
                step = self.act(
                    purpose = action_purpose,
                    tool = action_tool,
                    prompt = action_prompt,
                    disable_inference = disable_inference,
                )
                self.program_trace.append(str(step))
            elif current_node.labels[0] == "Decision":
                try:
                    decision_purpose = current_node.properties["name"]
                    decision_question = current_node.properties["question"]
                except ValueError:
                    raise RuntimeError("Decision node invalid: Missing a required parameter")
                options = []
                params = {"purpose": decision_purpose}
                result = self.get_current_program().query(
                    'MATCH (n:Decision {name:$purpose})-[r]->() RETURN type(r)',
                    params = params,
                )
                for record in result.result_set:
                    options.append(record[0])
                if len(options) == 0:
                    raise RuntimeError("Decision node invalid: No output edges detected")
                step = self.decide(
                    purpose = decision_purpose,
                    question = decision_question,
                    options = options,
                )
                if self.commit_decision:
                    self.program_trace.append(str(step))
            elif current_node.labels[0] == "Control":
                try:
                    control_flow = current_node.properties["name"]
                except ValueError:
                    raise RuntimeError("Control node invalid: Missing a required parameter")
                if control_flow == "End":
                    step = self.end_current_program()
                    if self.commit_program_flow:
                        self.program_trace.append(str(step))
                else:
                    raise RuntimeError(
                        "Invalid name for control node. Please verify your programs."
                    )
            else:
                raise RuntimeError(
                    "Invalid Node label used, should be Control, Action, Decision or Program, please verify your program"
                )
            return step
        return None

    def act(self, purpose: str, tool: str, prompt: str, disable_inference: bool = False) -> AgentAction:
        """The method to act"""
        if tool not in self.tools:
            raise ValueError(f"Invalid tool: '{tool}' does not exist, should be one of {list(self.tools.keys())}")
        if len(self.program_trace) > 0:
            trace = "\n".join(self.program_trace)
        else:
            trace = "Nothing done yet"
        prediction = self.tools[tool](
            objective = self.objective,
            purpose = purpose,
            trace = trace,
            prompt = prompt,
            disable_inference = disable_inference,
            stop = self.stop,
        )
        action = AgentAction(
            hop = self.current_hop,
            purpose = purpose,
            tool = tool,
            prompt = prompt,
            prediction = prediction,
        )
        self.set_current_node(self.get_next_node(self.get_current_node()))
        return action

    def decide(self, purpose: str, question:str, options: List[str]) -> AgentDecision:
        """The method to make a decision"""
        if len(self.program_trace) > 0:
            trace = "\n".join(self.program_trace)
        else:
            trace = "Nothing done yet"
        possible_answers = " or ".join(options)
        prediction = self.decision(
            trace = trace,
            purpose = purpose,
            question = question,
            options = possible_answers,
            stop = self.stop,
        )
        answer = prediction.answer.strip()
        dspy.Suggest(
            len(answer.split()) == 1,
            f"The Answer should be only ONE word between {possible_answers}"
        )
        print(answer)
        answer = answer.strip(".:;,")
        answer = answer.upper()
        params = {"purpose": purpose}
        result = self.get_current_program().query(
            'MATCH (:Decision {name:$purpose})-[:'+answer+']->(n) RETURN n',
            params = params,
        )
        next_node = result.result_set[0][0]
        decision = AgentDecision(
            hop = self.current_hop,
            purpose = purpose,
            question = question,
            options = options,
            answer = answer,
        )
        self.set_current_node(next_node)
        return decision

    def forward(self, **kwargs):
        """DSPy forward prediction"""
        self.start(kwargs["objective"])
        for i in range(self.max_iters):
            if not self.finished():
                self.run_step()
            else:
                break
        prediction = self.finish(
            trace = "\n".join(self.program_trace),
            objective = self.objective
        )
        return dspy.Prediction(
            final_answer = prediction.answer,
            program_trace = "\n".join(self.program_trace),
            finish_reason = "max iters" if i >= self.max_iters else "finished",
        )

    def get_next_node(self, node: Node, program: Optional[Graph] = None) -> Optional[Node]:
        """Method to get the next node"""
        try:
            name = node.properties["name"]
        except ValueError:
            raise RuntimeError("Invalid node: missing required parameter")
        params = {"name": name}
        if program is None:
            program = self.get_current_program()
        result = program.query(
            'MATCH ({name:$name})-[:NEXT]->(m) RETURN m',
            params=params,
        )
        if len(result.result_set) > 0:
            return result.result_set[0][0]
        return None

    def get_starting_node(self, program_name: str) -> Node:
        """Method to get the starting node of the given program"""
        program = self.program_memory.get_graph(program_name)
        result = program.query(
            'MATCH (n:Control {name:"Start"}) RETURN n')
        if len(result.result_set) == 0:
            raise RuntimeError("No entry point detected,"+
                " please make sure you loaded the programs.")
        if len(result.result_set) > 1:
            raise RuntimeError("Multiple entry point detected,"+
                " please correct your programs.")
        starting_node = result.result_set[0][0]
        return starting_node

    def get_current_program(self) -> Optional[Graph]:
        """Method to retreive the current program from the stack"""
        if len(self.program_stack) > 0:
            return self.program_stack[-1][1]
        return None

    def get_current_node(self) -> Optional[Node]:
        """Method to retreive the current node from the stack"""
        if len(self.program_stack) > 0:
            return self.program_stack[-1][0]
        return None
    
    def set_current_node(self, node: Node):
        """Method to set the current node from the stack"""
        if len(self.program_stack) > 0:
            _, program = self.program_stack[-1]
            self.program_stack[-1] = (node, program)

    def call_program(
        self,
        purpose: str,
        program_name: str,
    ) -> ProgramCall:
        """Call an existing program"""
        program_called = self.program_memory.get_graph(program_name)
        starting_node = self.get_starting_node(program_name)
        first_node = self.get_next_node(starting_node, program=program_called)
        self.program_stack.append((first_node, program_called))
        program_call = ProgramCall(
            hop = self.current_hop,
            purpose = purpose,
            program = program_name,
        )
        return program_call

    def end_current_program(self) -> ProgramEnd:
        """End the current program (pop the stack)"""
        program_name = self.get_current_program().name.split(":")[-1]
        self.program_stack.pop()
        if self.get_current_node() is not None:
            self.set_current_node(self.get_next_node(self.get_current_node()))
        program_end = ProgramEnd(
            hop = self.current_hop,
            program = program_name,
        )
        return program_end

    def start(self, objective: str):
        """Start the interpreter"""
        self.current_hop = 0
        self.objective = objective
        self.program_trace = []
        self.program_stack = deque()
        call_program = self.call_program(self.objective, self.entrypoint)
        self.program_trace.append(str(call_program))

    def stop(self):
        """Stop the interpreter"""
        self.current_hop = 0
        self.objective = "N/A"
        self.program_trace = []
        self.program_stack = deque()

    def finished(self):
        """Check if the program is finished"""
        return self.get_current_node() is None

    def __deepcopy__(self, memo):
        cpy = (type)(self)(
            program_memory = ProgramMemory(
                index_name = self.program_memory.index_name,
                graph_index = self.program_memory.graph_index,
                embeddings = self.program_memory.embeddings,
                hostname = self.program_memory.hostname,
                port = self.program_memory.port,
                username = self.program_memory.username,
                password = self.program_memory.password,
                indexed_label = self.program_memory.indexed_label,
            ),
        )
        cpy.tools = copy.deepcopy(self.tools)
        cpy.decision = copy.deepcopy(self.decision)
        cpy.finish = copy.deepcopy(self.finish)
        return cpy