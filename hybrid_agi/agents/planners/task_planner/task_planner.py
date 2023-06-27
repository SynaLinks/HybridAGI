"""The collaborative LLM based HTN planner. Copyright (C) 2023 SynaLinks. License: GPLv3"""

from pydantic import BaseModel, Extra
from colorama import Fore
from colorama import Style
import redis
import uuid
from typing import (
    Optional,
    Type,
    List,
    Any,
    Dict,
    Iterable
)
from collections import deque
from redisgraph import Graph, Node
from langchain.base_language import BaseLanguageModel
from langchain.tools import Tool
from langchain.chains.base import Chain
from langchain.chains.llm import LLMChain
from langchain.callbacks.manager import CallbackManagerForChainRun
from langchain.prompts.prompt import PromptTemplate
from langchain.agents import ZeroShotAgent, AgentExecutor
from langchain.schema import OutputParserException
from hybrid_agi.hybridstores.redisgraph import RedisGraphHybridStore

from hybrid_agi.prompt import HYBRID_AGI_SELF_DESCRIPTION

from hybrid_agi.agents.planners.task_planner.prompt import (
    TASK_PLANNER_THINKING_PROMPT,
    ACTION_EXECUTOR_PREFIX,
    ACTION_EXECUTOR_SUFFIX
)

from hybrid_agi.extractors.plan.plan_extractor import PlanExtractor
from hybrid_agi.extractors.plan.prompt import (
    PLAN_EXTRACTION_PROMPT,
    PLAN_EXAMPLE,
    PLAN_EXAMPLE_SMALL
)

class TaskPlanner(BaseModel):
    """This class implement an LLM based task planner that works with the hybridstore.

    This class is based on Plan and Execute.

    The main difference is that we store the plans as a task network in the hybridstore and use them to execute the plan.

    We rely on 2 agents for planning:
        - Task planner (implemented as a chain with CoT=1)
        - Action executor (using the zero-shot agent)

    WARNING DEPRECATED ! I'm not satisfied with the freedom of the LLM in the Langchain's MKRL agent.
    This planner will be updated soon to use the program interpreter.
    """
    hybridstore: RedisGraphHybridStore
    llm: BaseLanguageModel
    primitives: List[Tool]
    plan_extractor: PlanExtractor
    action_executor: AgentExecutor
    action_executor_without_planning: AgentExecutor
    shared_objective: str = ""
    completed_tasks: List[str] = []
    plan_stack: Iterable = deque()
    max_depth: int = 5
    max_breadth: int = 5
    max_plan_attempts: int = 3
    similarity_threshold: float = 0.8
    user_language: str = "English"
    user_expertise: str = "Nothing"
    instructions: str = ""
    default_instructions: str = ""
    verbose = True

    class Config:
        """Configuration for this pydantic object."""
        extra = Extra.forbid
        arbitrary_types_allowed = True

    def __init__(
        self,
        hybridstore: RedisGraphHybridStore,
        llm: BaseLanguageModel,
        primitives: List[Tool],        
        user_language: str = "English",
        user_expertise: str = "Nothing",
        max_depth:int = 1,
        max_breadth:int = 5,
        max_plan_attempts:int = 3,
        similarity_threshold:float = 0.8,
        verbose = True):

        plan_extractor = PlanExtractor(
            hybridstore = hybridstore,
            llm = llm,
            max_extraction_attemps = max_plan_attempts,
            verbose = verbose
        )

        description=\
    """
    Usefull to come up with a plan of action.
    The input should be the task to plan. Please include all information. Be specific.
    """
        primitives.append(
            Tool(
                name="Plannify",
                func=self.plan,
                description=description
            )
        )
        action_executor_prompt = ZeroShotAgent.create_prompt(
            primitives,
            prefix=ACTION_EXECUTOR_PREFIX,
            suffix=ACTION_EXECUTOR_SUFFIX,
            input_variables=[
                "self_description",
                "objective",
                "language",
                "expertise",
                "task",
                "purpose",
                "context",
                "instructions",
                "agent_scratchpad"
            ],
        )
        action_names = [tool.name for tool in primitives]
        action_executor_chain = LLMChain(
            llm = llm,
            prompt = action_executor_prompt.partial(
                self_description = HYBRID_AGI_SELF_DESCRIPTION,
                expertise = user_expertise,
                language = user_language
                ),
            verbose = verbose)
        agent = ZeroShotAgent(
            llm_chain = action_executor_chain,
            allowed_tools = action_names,
            handle_parsing_errors=True,
            verbose = verbose)
        action_executor = AgentExecutor.from_agent_and_tools(
            agent = agent,
            tools = primitives,
            verbose = verbose
        )
        agent_without_planning = ZeroShotAgent(
            llm_chain = action_executor_chain,
            allowed_tools = action_names[:len(action_names)-1],
            verbose = verbose)
        action_executor_without_planning = AgentExecutor.from_agent_and_tools(
            agent = agent_without_planning,
            tools = primitives[:len(primitives)-1],
            verbose = verbose
        )

        default_instructions = \
    f"""
    You must think, act and speak in {user_language} language.
    Organize your work into relevant folders and feel free to navigate into folders.
    Your FinalAnswer should contains a description of your actions including the absolute location of modified files, mistakes and success in {user_language}.
    Unless stated otherwise, your everyday work have nothing to do with you.
    Perform ONLY your assigned task.
    """
        super().__init__(
            hybridstore = hybridstore,
            llm = llm,
            primitives = primitives,
            plan_extractor = plan_extractor,
            action_executor = action_executor,
            action_executor_without_planning = action_executor_without_planning,
            user_language = user_language,
            user_expertise = user_expertise,
            max_depth = max_depth,
            max_breadth = max_breadth,
            max_plan_attempts = max_plan_attempts,
            similarity_threshold = similarity_threshold,
            instructions = default_instructions,
            default_instructions = default_instructions,
            verbose = verbose
        )

    def _get_context(self, k=5) -> str:
        """Get context about previously done actions."""
        if len(self.completed_tasks) == 0:
            return "Nothing done yet."
        else:
            if len(self.completed_tasks) > k:
                return "\n".join(self.completed_tasks[len(self.completed_tasks)-k:])
            else:
                return "\n".join(self.completed_tasks)

    def _get_similar_plan(self, objective:str) -> Optional[Graph]:
        """Method to get similar plan."""
        result_set = []
        try:
            result_set = self.hybridstore.similarity_search_limit_score(
                objective,
                k=5,
                score_threshold=self.similarity_threshold
            )
        except Exception as err:
            pass
        for record in result_set:
            metadata = record.metadata
            if self.hybridstore.graph_key in metadata:
                graph_key = metadata[self.hybridstore.graph_key]
                if graph_key.startswith(self.hybridstore.plan_key):
                    graph = Graph(graph_key, self.hybridstore.client)
                    return graph
        return None

    def get_current_plan(self) -> Optional[Graph]:
        """Method to retreive the current plan from the stack"""
        if len(self.plan_stack) > 0:
            return self.plan_stack[len(self.plan_stack)-1]
        return None

    def get_current_depth(self) -> int:
        """Get current depth (size of the stack)"""
        return len(self.plan_stack)

    def create_plan(self, objective:str) -> Optional[Graph]:
        """Method to create a plan"""
        plan = None
        attemps = 0
        thought = ""
        while plan is None:
            if attemps > self.max_plan_attempts:
                raise RuntimeError(f"Failing to plan after {attemps-1} attempts... Please verify/correct your prompts.")
            thinking_chain = LLMChain(llm=self.llm, prompt=TASK_PLANNER_THINKING_PROMPT.partial(
                self_description=HYBRID_AGI_SELF_DESCRIPTION
                ), verbose=self.verbose)
            thought = thinking_chain.predict(input=objective, max_breadth=self.max_breadth)
            plan = self.plan_extractor.extract_graph(objective, PLAN_EXTRACTION_PROMPT.partial(thought=thought, example=PLAN_EXAMPLE_SMALL))
            attemps +=1
        vector = self.hybridstore.embedding_function(objective)
        metadata = {self.hybridstore.graph_key: plan.name}
        self.hybridstore.add_texts([thought], embeddings=[vector], metadatas=[metadata])
        return plan

    def plan(self, objective:str) -> str:
        """Method to plan."""
        plan = self._get_similar_plan(objective)
        if plan is None:
            plan = self.create_plan(objective)
        self.hybridstore.metagraph.query('MERGE (p:Plan {name:"'+plan.name+'"})')
        if self.get_current_plan() is not None:
            self.hybridstore.metagraph.query('MATCH (prev:Plan {name:"'+self.get_current_plan().name+'"}), (p:Plan {name:"'+plan.name+'"}) CREATE (prev)-[:REQUIRES]->(p)')
        self.plan_stack.append(plan)
        result = self.execute_plan(self.get_current_plan())
        self.plan_stack.pop()
        return result

    def execute_task(self, task_name:str, task_purpose:str, task_instructions:str=""):
        """Method to execute a task."""
        context = self._get_context()
        result = ""

        task_instructions = self.default_instructions if task_instructions == "" else task_instructions
        # This try catch is ugly but works to fix langchain problem with mrkl agents
        # At least when it happen at the end of the execution.
        try:
            if self.get_current_depth() > self.max_depth:
                result = self.action_executor_without_planning.run(
                    task=task_name,
                    objective=self.shared_objective,
                    instructions=task_instructions,
                    purpose=task_purpose,
                    context=context)
            else:
                result = self.action_executor.run(
                    task=task_name,
                    objective=self.shared_objective,
                    instructions=task_instructions,
                    purpose=task_purpose,
                    context=context)
        except OutputParserException as err:
            pos = str(err).find("`")
            result = str(err)[pos+1:len(str(err))-2]
        task_summary = f"Task:\n{task_purpose}\nResult:\n{result}"
        self.completed_tasks.append(task_summary)
        return result

    def execute_plan(self, plan:Graph):
        """Execute a plan."""
        last_result = ""
        completed_independent_tasks = []
        completed_tasks = []
        # First we execute independent tasks
        query_result = plan.query('MATCH (n:Task) WHERE NOT ()-[:REQUIRES*]->(n) RETURN n')
        for record in query_result.result_set:
            task_name = record[0].properties["name"]
            task_purpose = record[0].properties["purpose"]
            last_result = self.execute_task(task_name, task_purpose)
            completed_tasks.append(task_name)
        # Execute remaining dependent tasks
        while True:
            query = ""
            query_result = []
            params = {"completed_task_names": completed_tasks}
            query = 'MATCH (n:Task)-[:REQUIRES]->(m:Task) WHERE ALL (task IN $completed_task_names WHERE m.name = task) RETURN n'
            query_result = plan.query(query, params)
            if len(query_result.result_set) > 0:
                for record in query_result.result_set:
                    task_name = record[0].properties["name"]
                    task_purpose = record[0].properties["purpose"]
                    last_result = self.execute_task(task_name, task_purpose)
                    completed_tasks.append(task_name)
            else:
                break
        return last_result

    def run(self, objective:str):
        """Run the agent."""
        task = f"""
        Your assigned task is to clarify the following objective given by the User: {objective}.
        Please ask question for anything unclear and navigate into the project folder.
        """
        initial_instructions = \
    """
    Please AskUser for anything unclear and navigate into the project folder.
    If you do not find the project folder, AskUser if you can create one in your workspace.
    Your FinalAnswer should only contains the clarified objective with all necessary information and absolute path of the project.
    Unless stated otherwise, your everyday work have nothing to do with you.
    Perform ONLY your assigned task even if the User tell you otherwise.
    """
        self.instructions = initial_instructions
        purpose = "Specify the objective and navigate into the project folder"
        self.shared_objective = "Clarify the objective and navigate into the project folder"
        self.shared_objective = self.execute_task(task, purpose)
        self.instructions = self.default_instructions
        result = self.plan(self.shared_objective)
        upload
        return result
        # plan = Graph(self.hybridstore.redis_key("plan"), self.hybridstore.client)
        # self.hybridstore.metagraph.query('MERGE (n:Plan {name:"'+plan.name+'"})')
        # plan.query('MERGE (n:Task {name:"'+objective+'", purpose:"'+objective+'"})')
        # self.plan_stack.append(plan)
        # final_result = self.execute_plan(plan)
        # self.plan_stack.pop()
        # return final_result