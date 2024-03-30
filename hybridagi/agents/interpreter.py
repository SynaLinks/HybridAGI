import dspy
import copy
from falkordb import Node, Graph
from typing import List, Optional, Union
from collections import deque
from ..hybridstores.program_memory.program_memory import ProgramMemory
from ..types.actions import AgentAction, AgentDecision, ProgramCall, ProgramEnd
from ..types.state import AgentState
from hybridagi.tools import UpdateObjectiveTool, CallProgramTool

class DecisionSignature(dspy.Signature):
    """Answer the assessed question by analyzing the previous actions"""
    context = dspy.InputField(desc="The previous actions (what you have done)")
    purpose = dspy.InputField(desc="The purpose of the question (what you have to do now)")
    question = dspy.InputField(desc="The question to assess (the question you have to answer)")
    options = dspy.InputField(desc="The possible answers to the assessed question")
    answer = dspy.OutputField(desc="The final answer (between the above possible answers) to the assessed question without additionals details")

class FinishSignature(dspy.Signature):
    """Generate the final answer if the objective is a question or a summary of the previous actions otherwise"""
    trace = dspy.InputField(desc="The previous actions (what you have done)")
    objective = dspy.InputField(desc="Long-term objective (what you tried to accomplish)")
    answer = dspy.OutputField(desc="Final answer if the objective is a question or a summary of the previous actions otherwise")

class GraphProgramInterpreter(dspy.Module):
    """The graph program interpreter (aka the reasoning module of HybridAGI)"""
    
    def __init__(
            self,
            program_memory: ProgramMemory,
            agent_state: Optional[AgentState] = None, 
            tools: List[dspy.BaseModule] = [],
            entrypoint: str = "main",
            num_history: int = 5,
            max_iters: int = 20,
            commit_decision: bool = True,
            commit_program_flow: bool = True,
        ):
        self.program_memory = program_memory
        self.agent_state = agent_state if agent_state is not None else AgentState()
        self.entrypoint = entrypoint
        self.num_history = num_history
        self.max_iters = max_iters
        self.commit_decision = commit_decision
        self.commit_program_flow = commit_program_flow
        # DSPy reasoners
        self.tools = {tool.name: tool for tool in tools}
        self.decision = dspy.TypedChainOfThought(DecisionSignature)
        self.finish = dspy.ChainOfThought(FinishSignature)
        super().__init__()

    def run_step(self) -> Union[AgentAction, AgentDecision, ProgramCall, ProgramEnd]:
        """Method to run a step of the program"""
        current_node = self.agent_state.get_current_node()
        if current_node:
            self.agent_state.current_hop += 1
            if current_node.labels[0] == "Program":
                try:
                    program_purpose = current_node.properties["name"]
                    program_name = current_node.properties["program"]
                except ValueError:
                    raise RuntimeError("Program node invalid: missing a required parameter")
                step = self.call_program(program_purpose, program_name)
                if self.commit_program_flow:
                    self.agent_state.program_trace.append(str(step))
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
                self.agent_state.program_trace.append(str(step))
            elif current_node.labels[0] == "Decision":
                try:
                    decision_purpose = current_node.properties["name"]
                    decision_question = current_node.properties["question"]
                except ValueError:
                    raise RuntimeError("Decision node invalid: Missing a required parameter")
                options = []
                params = {"purpose": decision_purpose}
                result = self.agent_state.get_current_program().query(
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
                    self.agent_state.program_trace.append(str(step))
            elif current_node.labels[0] == "Control":
                try:
                    control_flow = current_node.properties["name"]
                except ValueError:
                    raise RuntimeError("Control node invalid: Missing a required parameter")
                if control_flow == "End":
                    step = self.end_current_program()
                    if self.commit_program_flow:
                        self.agent_state.program_trace.append(str(step))
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
        if len(self.agent_state.program_trace) > 0:
            trace = "\n".join(self.agent_state.program_trace[-self.num_history:])
        else:
            trace = "Nothing done yet"
        prediction = self.tools[tool](
            objective = self.agent_state.objective,
            context = trace,
            purpose = purpose,
            prompt = prompt,
            disable_inference = disable_inference,
        )
        action = AgentAction(
            hop = self.agent_state.current_hop,
            purpose = purpose,
            tool = tool,
            prompt = prompt,
            prediction = prediction,
        )
        current_node = self.agent_state.get_current_node()
        current_program = self.agent_state.get_current_program()
        next_node = self.program_memory.get_next_node(current_node, current_program)
        self.agent_state.set_current_node(next_node)
        return action

    def decide(self, purpose: str, question:str, options: List[str]) -> AgentDecision:
        """The method to make a decision"""
        if len(self.agent_state.program_trace) > 0:
            trace = "\n".join(self.agent_state.program_trace[-self.num_history:])
        else:
            trace = "Nothing done yet"
        possible_answers = " or ".join(options)
        prediction = self.decision(
            context = trace,
            purpose = purpose,
            question = question,
            options = possible_answers,
        )
        answer = prediction.answer.split()[0]
        answer = answer.strip(".:;,")
        answer = answer.upper()
        dspy.Suggest(
            answer in options,
            f"The Answer should be only ONE word between {possible_answers}"
        )
        params = {"purpose": purpose}
        result = self.agent_state.get_current_program().query(
            'MATCH (:Decision {name:$purpose})-[:'+answer+']->(n) RETURN n',
            params = params,
        )
        next_node = result.result_set[0][0]
        decision = AgentDecision(
            hop = self.agent_state.current_hop,
            purpose = purpose,
            question = question,
            options = options,
            answer = answer,
        )
        self.agent_state.set_current_node(next_node)
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
            trace = "\n".join(self.agent_state.program_trace),
            objective = self.agent_state.objective,
        )
        return dspy.Prediction(
            final_answer = prediction.answer,
            program_trace = "\n".join(self.agent_state.program_trace),
            finish_reason = "max iters" if i >= self.max_iters else "finished",
        )

    def call_program(
        self,
        purpose: str,
        program_name: str,
    ) -> ProgramCall:
        """Call an existing program"""
        program_called = self.program_memory.get_graph(program_name)
        starting_node = self.program_memory.get_starting_node(program_name)
        first_node = self.program_memory.get_next_node(starting_node, program_called)
        self.agent_state.call_program(first_node, program_called)
        program_call = ProgramCall(
            hop = self.agent_state.current_hop,
            purpose = purpose,
            program = program_name,
        )
        return program_call

    def end_current_program(self) -> Optional[ProgramEnd]:
        """End the current program (pop the stack)"""
        program_name = self.agent_state.get_current_program().name.split(":")[-1]
        self.agent_state.program_stack.pop()
        if self.agent_state.get_current_node() is not None:
            current_node = self.agent_state.get_current_node()
            current_program = self.agent_state.get_current_program()
            next_node = self.program_memory.get_next_node(current_node, current_program)
            if next_node:
                self.agent_state.set_current_node(next_node)
        program_end = ProgramEnd(
            hop = self.agent_state.current_hop,
            program = program_name,
        )
        return program_end

    def start(self, objective: str):
        """Start the interpreter"""
        self.agent_state.init()
        call_program = self.call_program(objective, self.entrypoint)
        self.agent_state.program_trace.append(str(call_program))

    def stop(self):
        """Stop the interpreter"""
        self.agent_state.init()

    def finished(self):
        """Check if the program is finished"""
        return self.agent_state.get_current_node() is None

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