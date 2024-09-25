import dspy
from typing import Optional, List, Union
from colorama import Fore, Style
from jinja2 import Template
import json

from hybridagi.core.datatypes import (
    AgentStep,
    AgentStepType,
    AgentStepList,
    AgentOutput,
    AgentState,
    FinishReason,
    ToolInput,
    Message,
    InteractionSession,
)

from hybridagi.core.graph_program import (
    GraphProgram,
    Control,
    ControlType,
    Action,
    Decision,
    Program,
)

from hybridagi.modules.agents.tools.tool import Tool

from hybridagi.memory.program_memory import ProgramMemory
from hybridagi.memory.trace_memory import TraceMemory
from hybridagi.embeddings.embeddings import Embeddings

from hybridagi.core.datatypes import Query, QueryWithSession

from hybridagi.output_parsers import (
    DecisionOutputParser,
    PredictionOutputParser,
)

DECISION_COLOR = f"{Fore.BLUE}"
ACTION_COLOR = f"{Fore.CYAN}"
CONTROL_COLOR = f"{Fore.MAGENTA}"
FINISH_COLOR = f"{Fore.YELLOW}"
CHAT_COLOR = f"{Fore.GREEN}"

class DecisionSignature(dspy.Signature):
    """You will be given an objective, context, purpose, question and option your task is to infer the correct choice between the given options
    
    You answer should always start with the label choosed.
    """
    objective = dspy.InputField(desc = "The long-term objective (what you are doing)")
    context = dspy.InputField(desc = "The previous actions (what you have done)")
    purpose = dspy.InputField(desc = "The purpose of the decision (what you have to do now)")
    question = dspy.InputField(desc = "The decision-making question")
    options = dspy.InputField(desc = "The available options for the decision-making question")
    choice = dspy.OutputField(desc = "The best choice to the decision-making question", prefix="Choice:")

class CorrectDecisionSignature(dspy.Signature):
    """You will be given an answer, options tour task is to infer the choice among the options.
    
    Only choose one of the provided option and start your answer with the label choosed.
    """
    answer = dspy.InputField(desc = "The answer to assess")
    options = dspy.InputField(desc = "The available options")
    choice = dspy.OutputField(desc = "The correct choice", prefix="Choice:")

class GraphInterpreterAgent(dspy.Module):
    
    def __init__(
            self,
            program_memory: ProgramMemory,
            agent_state: AgentState,
            embeddings: Optional[Embeddings] = None,
            trace_memory: Optional[TraceMemory] = None,
            tools: List[Tool] = [],
            entrypoint: str = "main",
            num_history: int = 5,
            max_iters: int = 20,
            commit_decision_steps: bool = False,
            decision_lm: Optional[dspy.LM] = None,
            verbose: bool = True,
            debug: bool = False,
        ):
        """
        Initializes the Graph Interpreter Agent.

        Args:
            program_memory (ProgramMemory): The program memory to use for the agent.
            embeddings (Optional[Embeddings], optional): The embeddings to use for the agent. Defaults to None.
            trace_memory (Optional[TraceMemory], optional): The trace memory to use for the agent. Defaults to None.
            agent_state (Optional[AgentState], optional): The initial state of the agent. Defaults to None.
            tools (List[Tool], optional): The tools that the agent can use. Defaults to an empty list.
            entrypoint (str, optional): The name of the entrypoint program. Defaults to "main".
            num_history (int, optional): The number of previous steps to include in the agent's context. Defaults to 5.
            max_iters (int, optional): The maximum number of iterations of the agent. Defaults to 20.
            verbose (bool, optional): Whether to print verbose output. Defaults to True.
        """
        super().__init__()
        self.embeddings = embeddings
        self.program_memory = program_memory
        self.trace_memory = trace_memory
        self.agent_state = agent_state
        self.entrypoint = entrypoint
        self.num_history = num_history
        self.max_iters = max_iters
        self.decision_parser = DecisionOutputParser()
        self.prediction_parser = PredictionOutputParser()
        self.commit_decision_steps = commit_decision_steps
        self.decision_lm = decision_lm
        self.verbose = verbose
        self.debug = debug
        self.previous_agent_step = None
        if self.trace_memory is not None:
            if self.embeddings is None:
                raise ValueError("An embeddings should be provided when using the trace memory")
        # DSPy reasoners
        # The interpreter model used to navigate, only contains decision signatures
        # With that, DSPy should better optimize the graph navigation task
        self.decisions = [
            dspy.ChainOfThought(DecisionSignature) for i in range(0, self.max_iters)
        ]
        self.correct_decision = dspy.Predict(CorrectDecisionSignature)
        # Agent tools optimized by DSPy
        self.tools = {tool.name: tool for tool in tools}
    
    def run_step(self):
        """
        Runs a single step of the agent's execution.
        """
        current_step = self.agent_state.get_current_step()
        agent_step = None
        self.agent_state.current_hop += 1
        if isinstance(current_step, Program):
            agent_step = self.call_program(current_step)
            self.agent_state.program_trace.steps.append(str(agent_step))
            if self.verbose:
                print(f"{CONTROL_COLOR}{agent_step}{Style.RESET_ALL}")
        elif isinstance(current_step, Action):
            agent_step = self.act(current_step)
            self.agent_state.program_trace.steps.append(str(agent_step))
            if self.verbose:
                print(f"{ACTION_COLOR}{agent_step}{Style.RESET_ALL}")
        elif isinstance(current_step, Decision):
            agent_step = self.decide(current_step)
            if self.commit_decision_steps:
                self.agent_state.program_trace.steps.append(str(agent_step))
            if self.verbose:
                print(f"{DECISION_COLOR}{agent_step}{Style.RESET_ALL}")
        elif isinstance(current_step, Control):
            if current_step.id == "end":
                agent_step = self.end_current_program()
                # self.agent_state.program_trace.steps.append(str(agent_step))
                if self.verbose:
                    print(f"{CONTROL_COLOR}{agent_step}{Style.RESET_ALL}")
            else:
                raise RuntimeError("Invalid control node. Please verify your programs.")
        else:
            raise RuntimeError("Invalid step, should be Control, Action, Decision or Program, please verify your program")
        if self.trace_memory is not None:
            if agent_step is not None:
                if self.previous_agent_step is not None:
                    agent_step.parent_id = self.previous_agent_step.id
                self.previous_agent_step = agent_step
                self.trace_memory.update(agent_step)
    
    def start(self, query_or_query_with_session: Union[Query, QueryWithSession]) -> AgentStep:
        """
        Starts the agent's execution with the given query or query with session.

        Args:
            query_or_query_with_session (Union[Query, QueryWithSession]): The query or query with session to start the agent's execution with.

        Returns:
            AgentStep: The initial step of the agent's execution.
        """
        if isinstance(query_or_query_with_session, Query):
            self.agent_state.objective = query_or_query_with_session
            self.agent_state.session = InteractionSession()
            self.agent_state.session.chat.msgs.append(
                Message(role="User", content=query_or_query_with_session.query)
            )
        elif isinstance(query_or_query_with_session, QueryWithSession):
            query = query_or_query_with_session.query
            session = query_or_query_with_session.session
            self.agent_state.objective = query
            self.agent_state.session = session
            self.agent_state.session.chat.msgs.append(
                Message(role="User", content=query.query)
            )
        else:
            raise ValueError(f"Invalid input for {type(self).__name__} must be Query or QueryWithSession")
        self.previous_agent_step = None
        self.agent_state.current_hop = 0
        self.agent_state.decision_hop = 0
        self.agent_state.final_answer = ""
        self.agent_state.program_trace = AgentStepList()
        main_program = self.program_memory.get(self.entrypoint).progs[0]
        self.agent_state.call_program(main_program)
        agent_step = AgentStep(
            hop = self.agent_state.current_hop,
            step_type = AgentStepType.ProgramCall,
            inputs = {"purpose": self.agent_state.objective.query, "program": self.entrypoint},
        )
        if self.verbose:
            print(f"{CONTROL_COLOR}{agent_step}{Style.RESET_ALL}")
        self.agent_state.program_trace.steps.append(str(agent_step))
        if self.trace_memory is not None:
            self.previous_agent_step = agent_step
            self.trace_memory.update(agent_step)
        return agent_step
    
    def act(self, step: Action) -> AgentStep:
        """
        Executes the given action and returns the executed step.

        Args:
            step (Action): The action to execute.

        Returns:
            AgentStep: The executed Action step.
        """
        if len(self.agent_state.program_trace.steps) > 0:
            trace = "\n".join([str(s) for s in self.agent_state.program_trace.steps[-self.num_history:]])
            trace += "\n--- END OF TRACE ---"
        else:
            trace = "Nothing done yet"
        if step.tool not in self.tools:
            raise ValueError(f"Invalid tool: '{step.tool}' does not exist, should be one of {list(self.tools.keys())}")
        jinja_template = Template(step.prompt)
        prompt_kwargs = {}
        for key in step.var_in:
            if key in self.agent_state.variables:
                prompt_kwargs[key] = self.agent_state.variables[key]
            else:
                prompt_kwargs[key] = ""
        rendered_template = jinja_template.render(**prompt_kwargs)
        tool_input = ToolInput(
            objective = self.agent_state.objective.query,
            purpose = step.purpose,
            context = trace,
            prompt = rendered_template,
            disable_inference = step.disable_inference,
        )
        tool_output = self.tools[step.tool](
            tool_input = tool_input,
        )
        if step.var_out is not None:
            if len(dict(tool_output).keys()) > 1:
                self.agent_state.variables[output] = tool_output.to_dict()
            else:
                self.agent_state.variables[output] = tool_output.to_dict()[list(dict(tool_output).keys())[0]]
        agent_step = AgentStep(
            hop = self.agent_state.current_hop,
            step_type = AgentStepType.Action,
            inputs = dict(tool_input),
            outputs = tool_output.to_dict(),
        )
        if self.embeddings is not None and step.tool != "PastActionSearch":
            if len(dict(agent_step.outputs).keys()) > 1:
                embedded_string = json.dumps(agent_step.outputs)
            else:
                embedded_string = tool_output.to_dict()[list(tool_output.to_dict().keys())[0]]
            agent_step.vector = self.embeddings.embed_text(embedded_string)
        if step.tool != "CallGraphProgram":
            current_program = self.agent_state.get_current_program()
            current_step = self.agent_state.get_current_step()
            next_step = current_program.get_next_step(current_step.id)
            self.agent_state.set_current_step(next_step)
        return agent_step
        
    def decide(self, step: Decision) -> AgentStep:
        """
        Makes a decision based on the given decision step and returns the executed step.

        Args:
            step (Decision): The decision step to make a decision based on.

        Returns:
            AgentStep: The executed Decision step.
        """
        if len(self.agent_state.program_trace.steps) > 0:
            trace = "\n".join([str(s) for s in self.agent_state.program_trace.steps[-self.num_history:]])
            trace += "\n--- END OF TRACE ---"
        else:
            trace = "Nothing done yet"
        choices = self.agent_state.get_current_program().get_decision_choices(step.id)
        possible_answers = " or ".join(choices)
        with dspy.context(lm=self.decision_lm if self.decision_lm is not None else dspy.settings.lm):
            pred = self.decisions[self.agent_state.decision_hop](
                objective = self.agent_state.objective.query,
                context = trace,
                purpose = step.purpose,
                question = step.question,
                options = possible_answers,
            )
            pred.choice = pred.choice.replace("\"", "")
            pred.choice = self.prediction_parser.parse(pred.choice, prefix="Choice:", stop=["."])
            pred.choice = self.decision_parser.parse(pred.choice, options=choices)
            if pred.choice not in choices:
                corrected_pred = self.correct_decision(
                    answer = pred.choice,
                    options = possible_answers,
                )
                corrected_pred.choice = corrected_pred.choice.replace("\"", "")
                corrected_pred.choice = self.prediction_parser.parse(corrected_pred.choice, prefix="Choice:", stop=["."])
                corrected_pred.choice = self.decision_parser.parse(corrected_pred.choice, options=choices)
                pred.choice = corrected_pred.choice
        self.agent_state.decision_hop += 1
        agent_step = AgentStep(
            hop = self.agent_state.current_hop,
            step_type = AgentStepType.Decision,
            inputs = {"purpose": step.purpose, "question": step.question, "options": choices},
            outputs = {"choice": pred.choice},
        )
        next_step = self.agent_state.get_current_program().get_decision_next_step(step.id, pred.choice)
        self.agent_state.set_current_step(next_step)
        return agent_step
    
    def call_program(self, step: Program) -> AgentStep:
        """
        Calls the given program and returns the executed step.

        Args:
            step (Program): The program step.

        Returns:
            AgentStep: The executed ProgramCall step.
        """
        current_program = self.agent_state.get_current_program()
        next_step = current_program.get_next_step(step.id)
        if next_step is not None:
            self.agent_state.set_current_step(next_step)
        graph_program = self.program_memory.get(step.program).progs[0]
        self.agent_state.call_program(graph_program)
        agent_step = AgentStep(
            hop = self.agent_state.current_hop,
            step_type = AgentStepType.ProgramCall,
            inputs = {"purpose": step.purpose, "program": step.program},
        )
        return agent_step
    
    def end_current_program(self) -> AgentStep:
        """
        Ends the current program and returns the executed step.

        Returns:
            AgentStep: The executed ProgramEnd step.
        """
        current_step = self.agent_state.get_current_step()
        current_program = self.agent_state.get_current_program()
        agent_step = AgentStep(
            hop = self.agent_state.current_hop,
            step_type = AgentStepType.ProgramEnd,
            inputs = {"program": current_program.name},
        )
        self.agent_state.end_program()
        return agent_step

    def finished(self):
        """
        Checks if the agent's execution is finished.

        Returns:
            bool: True if the agent's execution is finished, False otherwise.
        """
        return len(self.agent_state.program_stack) == 0
    
    def forward(self, query_or_query_with_session: Union[Query, QueryWithSession]) -> AgentOutput:
        """
        The DSPy forward method to execute the programs into memory

        Args:
            query_or_query_with_session (Union[Query, QueryWithSession]): The query or query with session to start the agent's execution with.

        Returns:
            AgentOutput: The output of the agent's execution.
        """
        self.start(query_or_query_with_session)
        for i in range(self.max_iters):
            if self.debug is False:
                try:
                    self.run_step()
                except Exception as e:
                    return AgentOutput(
                        finish_reason = FinishReason.Error,
                        final_answer = "Error occured: "+str(e),
                        program_trace = self.agent_state.program_trace,
                        session = self.agent_state.session,
                    )
            else:
                self.run_step()
            if self.finished():
                return AgentOutput(
                    finish_reason = FinishReason.Finished,
                    final_answer = self.agent_state.final_answer,
                    program_trace = self.agent_state.program_trace,
                    session = self.agent_state.session,
                )
        return AgentOutput(
            finish_reason = FinishReason.MaxIters,
            final_answer = self.agent_state.final_answer,
            program_trace = self.agent_state.program_trace,
            session = self.agent_state.session,
        )