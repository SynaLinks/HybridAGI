"""The interpreter. Copyright (C) 2024 SynaLinks. License: GPL-3.0"""

import random
import dspy
import json
import copy
from colorama import Fore, Style
from falkordb import Node, Graph
from typing import List, Optional, Union
from collections import deque
from ..hybridstores.program_memory.program_memory import ProgramMemory
from ..hybridstores.trace_memory.trace_memory import TraceMemory
from ..types.actions import AgentAction, AgentDecision, ProgramCall, ProgramEnd
from ..types.state import AgentState
from ..output_parsers.decision import DecisionOutputParser
from ..output_parsers.prediction import PredictionOutputParser

random.seed(123)

DECISION_COLOR = f"{Fore.BLUE}"
ACTION_COLOR = f"{Fore.CYAN}"
CONTROL_COLOR = f"{Fore.MAGENTA}"
FINISH_COLOR = f"{Fore.YELLOW}"
CHAT_COLOR = f"{Fore.GREEN}"

class DecisionSignature(dspy.Signature):
    """You will be given an objective, purpose and context
    Using the question and options, you will infer the correct label"""
    objective = dspy.InputField(desc = "The long-term objective (what you are doing)")
    context = dspy.InputField(desc = "The context (what you have done)")
    purpose = dspy.InputField(desc = "The purpose of the question (what you have to do now)")
    question = dspy.InputField(desc = "The question to assess")
    labels = dspy.InputField(desc = "The possible labels to the assessed question")
    correct_label = dspy.OutputField(desc = "The correct label", prefix="Label:")

class AnswerToLabel(dspy.Signature):
    """Classify the answer between the possible labels"""
    answer = dspy.InputField(desc = "The answer to assess")
    labels = dspy.InputField(desc = "The possible labels")
    correct_label = dspy.OutputField(desc = "The correct label", prefix="Label:")

class PredictSignature(dspy.Signature):
    """You will be given an objective, purpose and context
    Using the prompt to help you, you will infer the correct answer."""
    objective = dspy.InputField(desc = "The long-term objective (what you are doing)")
    context = dspy.InputField(desc = "The previous actions (what you have done)")
    purpose = dspy.InputField(desc = "The purpose of the action (what you have to do now)")
    prompt = dspy.InputField(desc = "The action specific instructions (How to do it)")
    answer = dspy.OutputField(desc = "The right answer with the right format")

class FinishSignature(dspy.Signature):
    """You will be given an objective, and trace
    Using the trace, you will infer the correct answer to the objective's question or a summary of what have been done.
    If the answer is not in the trace, just say that you don't know."""
    trace = dspy.InputField(desc="The previous actions (what you have done)")
    objective = dspy.InputField(desc="Long-term objective (what you tried to accomplish or answer)")
    answer = dspy.OutputField(desc="The answer to the objective's question")

class GraphProgramInterpreter(dspy.Module):
    """The graph program interpreter (aka the reasoning module of HybridAGI)"""
    
    def __init__(
            self,
            program_memory: ProgramMemory,
            trace_memory: Optional[TraceMemory] = None,
            agent_state: Optional[AgentState] = None,
            tools: List[dspy.BaseModule] = [],
            entrypoint: str = "main",
            num_history: int = 5,
            max_iters: int = 20,
            add_final_step: bool = True,
            commit_decision_steps: bool = True,
            commit_program_flow_steps: bool = True,
            return_final_answer: bool = True,
            return_program_trace: bool = True,
            return_chat_history: bool = True,
            verbose: bool = True,
        ):
        super().__init__()
        self.program_memory = program_memory
        self.trace_memory = trace_memory
        self.agent_state = agent_state if agent_state is not None else AgentState()
        self.entrypoint = entrypoint
        self.num_history = num_history
        self.max_iters = max_iters
        self.add_final_step = add_final_step
        self.commit_decision_steps = commit_decision_steps
        self.commit_program_flow_steps = commit_program_flow_steps
        self.decision_parser = DecisionOutputParser()
        self.prediction_parser = PredictionOutputParser()
        self.return_final_answer = return_final_answer
        self.return_program_trace = return_program_trace
        self.return_chat_history = return_chat_history
        self.verbose = verbose
        # DSPy reasoners
        # The interpreter model used to navigate, only contains decision signatures
        # With that, DSPy should better optimize the graph navigation task
        self.decision_hop = 0
        self.decisions = [
            dspy.ChainOfThought(DecisionSignature) for i in range(0, self.max_iters)
        ]
        self.correct_decision = dspy.Predict(AnswerToLabel)
        # Agent tools optimized by DSPy
        self.tools = {tool.name: tool for tool in tools}
        # Finish signature optimized by DSPy
        self.finish = dspy.Predict(FinishSignature)

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
                if self.trace_memory:
                    self.trace_memory.commit(step)
                if self.commit_program_flow_steps:
                    self.agent_state.program_trace.append(str(step))
                    if self.verbose:
                        print(f"{CONTROL_COLOR}{step}{Style.RESET_ALL}")
            elif current_node.labels[0] == "Action":
                try:
                    action_purpose = current_node.properties["name"]
                    action_tool = current_node.properties["tool"]
                    if "prompt" in current_node.properties:
                        action_prompt = current_node.properties["prompt"]
                    else:
                        action_prompt = ""
                    if "disable_inference" in current_node.properties:
                        disable_inference = current_node.properties["disable_inference"].lower() == "true"
                    else:
                        disable_inference = False
                    if "output" in current_node.properties:
                        output = current_node.properties["output"]
                    else:
                        output = ""
                    if "inputs" in current_node.properties:
                        inputs = current_node.properties["inputs"]
                    else:
                        inputs = []
                except ValueError:
                    raise RuntimeError("Action node invalid: missing a required parameter")
                step = self.act(
                    purpose = action_purpose,
                    tool = action_tool,
                    prompt = action_prompt,
                    disable_inference = disable_inference,
                    inputs = inputs,
                    output = output,
                )
                self.agent_state.program_trace.append(str(step))
                if self.trace_memory:
                    self.trace_memory.commit(step)
                if self.verbose:
                    print(f"{ACTION_COLOR}{step}{Style.RESET_ALL}")
            elif current_node.labels[0] == "Decision":
                try:
                    decision_purpose = current_node.properties["name"]
                    decision_question = current_node.properties["question"]
                    if "inputs" in current_node.properties:
                        inputs = current_node.properties["inputs"]
                    else:
                        inputs = []
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
                    inputs = inputs,
                )
                if self.trace_memory:
                    self.trace_memory.commit(step)
                if self.commit_decision_steps:
                    self.agent_state.program_trace.append(str(step))
                    if self.verbose:
                        print(f"{DECISION_COLOR}{step}{Style.RESET_ALL}")
            elif current_node.labels[0] == "Control":
                try:
                    control_flow = current_node.properties["name"]
                except ValueError:
                    raise RuntimeError("Control node invalid: Missing a required parameter")
                if control_flow == "End":
                    step = self.end_current_program()
                    if step is not None:
                        if self.trace_memory:
                            self.trace_memory.commit(step)
                        if self.commit_program_flow_steps:
                            self.agent_state.program_trace.append(str(step))
                            if self.verbose:
                                print(f"{CONTROL_COLOR}{step}{Style.RESET_ALL}")
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

    def act(
            self,
            purpose: str,
            tool: str,
            prompt: str,
            disable_inference: bool = False,
            inputs: List[str] = [],
            output: str = "",
        ) -> AgentAction:
        """The method to act"""
        if tool not in self.tools and tool != "Predict":
            raise ValueError(f"Invalid tool: '{tool}' does not exist, should be one of {list(self.tools.keys())}")
        if len(self.agent_state.program_trace) > 0:
            trace = "\n".join(self.agent_state.program_trace[-self.num_history:])
        else:
            trace = "Nothing done yet"
        for i in inputs:
            if i in self.agent_state.variables:
                prompt = prompt.replace("{"+i+"}", str(self.agent_state.variables[i]))
            else:
                pass # TODO add a warning/exception when the variable is not populated?
        prediction = self.tools[tool](
            objective = self.agent_state.objective,
            context = trace,
            purpose = purpose,
            prompt = prompt,
            disable_inference = disable_inference,
        )
        if output:
            if prediction is not None:
                if len(dict(prediction).keys()) > 1:
                    self.agent_state.variables[output] = json.dumps(dict(prediction))
                else:
                    self.agent_state.variables[output] = dict(prediction)[list(dict(prediction).keys())[0]]
        action = AgentAction(
            hop = self.agent_state.current_hop,
            objective = self.agent_state.objective,
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

    def decide(self, purpose: str, question:str, options: List[str], inputs: List[str] = []) -> AgentDecision:
        """The method to make a decision"""
        random.shuffle(options)
        if len(self.agent_state.program_trace) > 0:
            trace = "\n".join(self.agent_state.program_trace[-self.num_history:])
        else:
            trace = "Nothing done yet"
        possible_answers = " or ".join(options)
        for i in inputs:
            if i in self.agent_state.variables:
                prompt = prompt.replace("{"+i+"}", self.agent_state.variables[i])
            else:
                pass # TODO add a warning/exception ?
        pred = self.decisions[self.decision_hop](
            objective = self.agent_state.objective,
            context = trace,
            purpose = purpose,
            question = question,
            labels = possible_answers,
        )
        pred.correct_label = self.prediction_parser.parse(pred.correct_label, prefix="Label:", stop=["."])
        pred.correct_label = self.decision_parser.parse(pred.correct_label, options=options)
        if pred.correct_label not in options:
            label = self.correct_decision(
                answer = pred.correct_label,
                labels = possible_answers,
            )
            label.correct_label = self.prediction_parser.parse(label.correct_label, prefix="Label:", stop=["."])
            label.correct_label = self.decision_parser.parse(label.correct_label, options=options)
            pred.correct_label = label.correct_label
        dspy.Assert(
            pred.correct_label in options,
            f"Selected Label should be only ONE of the following label: {possible_answers} Got '{pred.correct_label}' instead.\n"
        )
        self.decision_hop += 1
        params = {"purpose": purpose}
        result = self.agent_state.get_current_program().query(
            'MATCH (:Decision {name:$purpose})-[:'+pred.correct_label+']->(n) RETURN n',
            params = params,
        )
        next_node = result.result_set[0][0]
        decision = AgentDecision(
            hop = self.agent_state.current_hop,
            objective = self.agent_state.objective,
            purpose = purpose,
            question = question,
            options = options,
            answer = pred.correct_label,
            log = pred.rationale,
        )
        self.agent_state.set_current_node(next_node)
        return decision

    def forward(self, objective: str):
        """DSPy forward prediction"""
        self.start(objective)
        for i in range(self.max_iters):
            if not self.finished():
                self.run_step()
            else:
                break
        if self.return_final_answer:
            if self.add_final_step:
                prediction = self.finish(
                    trace = "\n".join(self.agent_state.program_trace),
                    objective = self.agent_state.objective,
                )
                final_answer = self.prediction_parser.parse(prediction.answer, prefix="Answer:", stop=["---"])
                self.agent_state.chat_history.append(
                    {"role": "AI", "message": final_answer}
                )
            else:
                final_answer = ""
                l = len(self.agent_state.chat_history)
                for i in range(l):
                    if self.agent_state.chat_history[-i]["role"] == "AI":
                        final_answer = self.agent_state.chat_history[-i]["message"]
                        break
        else:
            final_answer = ""

        if self.return_chat_history:
            chat_history = json.dumps(self.agent_state.chat_history, indent=2)
        else:
            chat_history = ""
        
        if self.return_program_trace:
            program_trace = "\n".join(self.agent_state.program_trace)
        else:
            program_trace = ""

        if self.verbose:
            if self.return_final_answer:
                print(f"{FINISH_COLOR}Final Answer:\n\n{final_answer}{Style.RESET_ALL}")
            if self.return_chat_history:
                print(f"{CHAT_COLOR}Chat History:\n\n{chat_history}{Style.RESET_ALL}")
        return dspy.Prediction(
            final_answer = final_answer,
            chat_history = chat_history,
            program_trace = program_trace,
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
        self.decision_hop = 0
        self.agent_state.chat_history.append(
            {"role": "User", "message": objective}
        )
        self.agent_state.objective = objective
        first_step = self.call_program(objective, self.entrypoint)
        self.agent_state.program_trace.append(str(first_step))
        if self.trace_memory:
            self.trace_memory.start_new_trace()
            self.trace_memory.commit(first_step)
        if self.verbose:
            print(f"{CONTROL_COLOR}{first_step}{Style.RESET_ALL}")

    def stop(self):
        """Stop the interpreter"""
        self.agent_state.init()

    def finished(self):
        """Check if the program is finished"""
        return self.agent_state.get_current_node() is None

    def __deepcopy__(self, memo):
        cpy = (type)(self)(
            program_memory = self.program_memory,
            trace_memory = self.trace_memory,
            agent_state = self.agent_state,
            commit_decision_steps = self.commit_decision_steps,
            commit_program_flow_steps = self.commit_program_flow_steps,
            add_final_step = self.add_final_step,
            return_chat_history = self.return_chat_history,
            return_final_answer = self.return_final_answer,
            return_program_trace = self.return_program_trace,
            verbose = self.verbose,
        )
        cpy.agent_state.init()
        cpy.tools = copy.deepcopy(self.tools)
        cpy.decisions = copy.deepcopy(self.decisions)
        cpy.finish = copy.deepcopy(self.finish)
        return cpy