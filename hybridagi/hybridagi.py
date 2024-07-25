import dspy
import os
from dspy.teleprompt import BootstrapFewShot, BootstrapFewShotWithRandomSearch
from typing import List, Optional, Dict, Any, Callable
from .tools.base import BaseTool
from .agents.interpreter import GraphProgramInterpreter
from .embeddings.base import BaseEmbeddings
from .embeddings.sentence_transformer import SentenceTransformerEmbeddings
from .hybridstores.program_memory.program_memory import ProgramMemory
from .hybridstores.trace_memory.trace_memory import TraceMemory
from .hybridstores.filesystem.filesystem import FileSystem
from .hybridstores.fact_memory.fact_memory import FactMemory
from .types.state import AgentState

from .knowledge_parsers.text import TextKnowledgeParser

from .loaders.graph_programs import GraphProgramsLoader
from .loaders.knowledge import KnowledgeLoader

from .tools import (
    AppendFileTool,
    AskUserTool,

    BrowseWebsiteTool,

    CallProgramTool,
    ClearTraceTool,
    CodeInterpreterTool,

    DocumentSearchTool,
    DuckDuckGoSearchTool,

    EntitySearchTool,

    InternalShellTool,

    PastActionSearchTool,
    PredictTool,
    ProgramSearchTool,

    QueryFactsTool,

    ReadFileTool,
    ReadProgramTool,
    ReadUserProfileTool,
    RevertTraceTool,

    SpeakTool,

    UpdateObjectiveTool,
    UpdateUserProfileTool,
    UploadTool,

    WriteFileTool,
    WriteProgramTool,
)

class HybridAGI():
    """Wrapper around HybridAGI logic"""

    def __init__(
            self,
            agent_name: str,
            hostname: str = "localhost",
            port: int = 6379,
            username: str = "",
            password: str = "",
            tools: List[BaseTool] = [],
            embeddings: Optional[BaseEmbeddings] = None,
            agent_state: Optional[AgentState] = None,
            program_memory: Optional[ProgramMemory] = None,
            filesystem: Optional[FileSystem] = None,
            trace_memory: Optional[TraceMemory] = None,
            fact_memory: Optional[FactMemory] = None,
            load_native_tools: bool = True,
            user_profile: str = "An average User",
            downloads_directory: str = "",
            wipe_on_start: bool = True,
            num_history: int = 5,
            max_iters: int = 20,
            add_final_step: bool = False,
            commit_decision_steps: bool = False,
            commit_program_flow_steps: bool = True,
            return_final_answer: bool = True,
            return_program_trace: bool = True,
            return_chat_history: bool = True,
            verbose: bool = True,
        ):
        self.agent_name = agent_name
        self.verbose = verbose
        self.user_profile = user_profile
        self.downloads_directory = downloads_directory

        if embeddings is None:
            self.embeddings = SentenceTransformerEmbeddings(
                dim = 384,
                model_name_or_path = "sentence-transformers/all-MiniLM-L6-v2",
            )
        else:
            self.embeddings = embeddings

        if agent_state is None:
            self.agent_state = AgentState()

        if program_memory is None:
            self.program_memory = ProgramMemory(
                hostname = hostname,
                port = port,
                username = username,
                password = password,
                index_name = self.agent_name,
                embeddings = self.embeddings,
                wipe_on_start = wipe_on_start,
            )
        else:
            self.program_memory = program_memory

        if trace_memory is None:
            self.trace_memory = TraceMemory(
                hostname = hostname,
                port = port,
                username = username,
                password = password,
                index_name = self.agent_name,
                embeddings = self.embeddings,
                wipe_on_start = wipe_on_start,
            )
        else:
            self.trace_memory = trace_memory

        if filesystem is None:
            self.filesystem = FileSystem(
                hostname = hostname,
                port = port,
                username = username,
                password = password,
                index_name = self.agent_name,
                embeddings = self.embeddings,
                wipe_on_start = wipe_on_start,
            )
        else:
            self.filesystem = filesystem

        if fact_memory is None:
            self.fact_memory = FactMemory(
                hostname = hostname,
                port = port,
                username = username,
                password = password,
                index_name = self.agent_name,
                embeddings = self.embeddings,
                wipe_on_start = wipe_on_start,
            )
        else:
            self.fact_memory = fact_memory

        self.graph_programs_loader = GraphProgramsLoader(
            program_memory = self.program_memory,
        )

        parsers = [
            TextKnowledgeParser(
                filesystem = self.filesystem,
                fact_memory = self.fact_memory,
            ),
        ]

        self.knowledge_loader = KnowledgeLoader(
            filesystem = self.filesystem,
            fact_memory = self.fact_memory,
            parsers = parsers,
        )

        if load_native_tools:
            self.tools = [
                AppendFileTool(
                    filesystem = self.filesystem,
                    agent_state = self.agent_state,
                ),
                AskUserTool(
                    agent_state = self.agent_state,
                ),
                BrowseWebsiteTool(),
                CallProgramTool(
                    program_memory = self.program_memory,
                    agent_state = self.agent_state,
                ),
                ClearTraceTool(
                    agent_state = self.agent_state
                ),
                CodeInterpreterTool(),
                DocumentSearchTool(
                    filesystem = self.filesystem,
                    embeddings = self.embeddings,
                ),
                DuckDuckGoSearchTool(),
                EntitySearchTool(
                    fact_memory = self.fact_memory,
                    embeddings = self.embeddings,
                ),
                InternalShellTool(
                    filesystem = self.filesystem,
                    agent_state = self.agent_state,
                ),
                PastActionSearchTool(
                    trace_memory = self.trace_memory,
                    embeddings = self.embeddings,
                ),
                PredictTool(),
                ProgramSearchTool(
                    program_memory = self.program_memory,
                    embeddings = self.embeddings,
                ),
                QueryFactsTool(
                    fact_memory = self.fact_memory,
                ),
                ReadFileTool(
                    filesystem = self.filesystem,
                    agent_state = self.agent_state,
                ),
                ReadProgramTool(
                    program_memory = self.program_memory,
                ),
                ReadUserProfileTool(
                    agent_state = self.agent_state,
                ),
                RevertTraceTool(
                    agent_state = self.agent_state,
                ),
                SpeakTool(
                    agent_state = self.agent_state,
                ),
                UpdateObjectiveTool(
                    agent_state = self.agent_state,
                ),
                UploadTool(
                    filesystem = self.filesystem,
                    agent_state = self.agent_state,
                    downloads_directory = self.downloads_directory
                ),
                WriteFileTool(
                    filesystem = self.filesystem,
                    agent_state = self.agent_state,
                ),
                WriteProgramTool(
                    program_memory = self.program_memory,
                ),
            ]
        else:
            self.tools = []
        self.tools.extend(tools)

        self.interpreter = GraphProgramInterpreter(
            program_memory = self.program_memory,
            trace_memory = self.trace_memory,
            agent_state = self.agent_state,
            tools = self.tools,
            num_history = num_history,
            max_iters = max_iters,
            add_final_step = add_final_step,
            commit_decision_steps = commit_decision_steps,
            commit_program_flow_steps = commit_program_flow_steps,
            return_final_answer = return_final_answer,
            return_program_trace = return_program_trace,
            return_chat_history = return_chat_history,
            verbose = verbose,
        ).activate_assertions()

    def add_tools(self, tools: List[BaseTool]):
        self.tools.extend(tools)

    def add_programs_from_folders(self, folders: List[str]):
        self.graph_programs_loader.from_folders(folders)

    def add_knowledge_from_folders(self, folders: List[str]):
        self.knowledge_loader.from_folders(folders)

    def execute(self, objective: str, user_profile: str = "An average user", verbose: bool = False):
        self.interpreter.verbose = verbose
        prediction = self.interpreter(objective, user_profile = user_profile)
        self.interpreter.verbose = self.verbose
        return prediction

    def optimize(
            self,
            trainset: List[dspy.Example],
            valset: List[dspy.Example],
            metric: Callable,
            teacher_lm: Optional[dspy.LM] = None,
            epochs: int = 2,
            num_threads: int = 1,
            max_bootstrapped_demos: int = 2,
            num_candidate_programs: int = 10,
            save_checkpoints: bool = True,
            verbose: bool = False,
        ):
        config = dict(
            max_bootstrapped_demos = max_bootstrapped_demos,
            max_labeled_demos = 0,
        )
        if len(trainset) <= max_bootstrapped_demos:
            optimizer = BootstrapFewShot(
                teacher_settings=dict({'lm': teacher_lm if teacher_lm is not None else dspy.settings.lm}),
                metric = metric,
                **config,
            )
        else:
            optimizer = BootstrapFewShotWithRandomSearch(
                num_threads = num_threads,
                num_candidate_programs = num_candidate_programs,
                teacher_settings=dict({'lm': teacher_lm if teacher_lm is not None else dspy.settings.lm}),
                metric = metric,
                **config,
            )
        self.interpreter.verbose = verbose

        evaluate = dspy.evaluate.Evaluate(
            devset = valset,
            metric = metric,
            num_threads = 1,
            display_progress = True,
            display_table = False,
        )
        print(f"Evaluating the baseline...")
        try:
            baseline_score = evaluate(self.interpreter)
        except Exception as e:
            baseline_score = 0.0
        print(f"Baseline score: {baseline_score}")
        if baseline_score < 100.0:
            current_score = baseline_score
            for epoch in range(1, epochs):
                print(f"Epoch {epoch}/{epochs}")
                print("Optimizing the underlying prompts...")
                if len(trainset) <= max_bootstrapped_demos:
                    compiled_interpreter = optimizer.compile(
                        self.interpreter,
                        trainset = trainset,
                    )
                else:
                    compiled_interpreter = optimizer.compile(
                        self.interpreter,
                        trainset = trainset,
                        valset = valset,
                    )
                try:
                    print("Evaluating the optimized program...")
                    new_score = evaluate(compiled_interpreter)
                except Exception:
                    new_score = 0.0
                print(f"Optimized score: {new_score}")
                if new_score >= current_score:
                    print(f"Saving checkpoint...")
                    print(f"Checkpoint saved at '{self.agent_name}.json'")
                    self.interpreter = compiled_interpreter
                    self.interpreter.save(self.agent_name+".json")
                    if new_score == 100.0:
                        break
                    current_score = new_score
            print("Optimization finished")
        else:
            print("Optimization aborted, validation dataset not difficult enough")
        self.interpreter.verbose = self.verbose

    def load(self, filename: str = ""):
        if not filename:
            filename = self.agent_name+".json"
        if os.path.exists(filename):
            self.interpreter.load(filename)
