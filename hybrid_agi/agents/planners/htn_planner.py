## The collaborative LLM based HTN planner.
## Copyright (C) 2023 SynaLinks.
##
## This program is free software: you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with this program. If not, see <https://www.gnu.org/licenses/>.

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

from hybrid_agi.prompt import (
    HYBRID_AGI_SELF_DESCRIPTION,
    HYBRID_AGI_CORE_VALUES
)

from hybrid_agi.agents.planners.prompt import (
    TASK_PLANNER_THINKING_PROMPT,
    PRIMITIVE_EXECUTOR_PREFIX,
    PRIMITIVE_EXECUTOR_SUFFIX
)

from hybrid_agi.extractors.plan.plan_extractor import PlanExtractor
from hybrid_agi.extractors.plan.prompt import (
    PLAN_EXTRACTION_PROMPT,
    PLAN_EXAMPLE,
    PLAN_EXAMPLE_SMALL
)

class HTNPlanner(BaseModel):
    """This class implement an Autonomous LLM based HTN planner.

    This program is based on BabyAGI work and collaborative HTN planning concepts.

    The main differences is that we store the plans as hierarchical task network and keep track of the trees-of-plans in the metagraph.

    We rely on 2 agents for planning:
        - Task planner (implemented as a chain with CoT=1)
        - Primitive executor (using the zero-shot agent)
    """
    hybridstore: RedisGraphHybridStore
    llm: BaseLanguageModel
    primitives: List[Tool]
    plan_extractor: PlanExtractor
    primitive_executor: AgentExecutor
    primitive_executor_without_planning: AgentExecutor
    shared_objective: str = ""
    completed_tasks: List[str] = []
    plan_stack: Iterable = deque()
    max_depth: int = 5
    max_breadth: int = 5
    max_plan_attempts: int = 3
    similarity_threshold: float = 0.8
    user_language: str = "English"
    user_expertise: str = "Nothing"
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
        max_depth:int = 5,
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
    Usefull when confronted to challenging tasks.
    The input should be the intended goal for planning.
    """
        primitives.append(
            Tool(
                name="Plannify",
                func=self.plan,
                description=description
            )
        )
        primitive_executor_prompt = ZeroShotAgent.create_prompt(
            primitives,
            prefix=PRIMITIVE_EXECUTOR_PREFIX,
            suffix=PRIMITIVE_EXECUTOR_SUFFIX,
            input_variables=[
                "self_description",
                "core_values",
                "objective",
                "language",
                "expertise",
                "task",
                "purpose",
                "context",
                "agent_scratchpad"
            ],
        )
        primitive_names = [tool.name for tool in primitives]
        primitive_executor_chain = LLMChain(
            llm = llm,
            prompt = primitive_executor_prompt.partial(
                self_description = HYBRID_AGI_SELF_DESCRIPTION,
                core_values = HYBRID_AGI_CORE_VALUES,
                expertise = user_expertise,
                language = user_language
                ),
            verbose = verbose)
        agent = ZeroShotAgent(
            llm_chain = primitive_executor_chain,
            allowed_tools = primitive_names,
            verbose = verbose)
        primitive_executor = AgentExecutor.from_agent_and_tools(
            agent = agent,
            tools = primitives,
            verbose = verbose
        )
        agent_without_planning = ZeroShotAgent(
            llm_chain = primitive_executor_chain,
            allowed_tools = primitive_names[:len(primitive_names)-1],
            verbose = verbose)
        primitive_executor_without_planning = AgentExecutor.from_agent_and_tools(
            agent = agent_without_planning,
            tools = primitives[:len(primitives)-1],
            verbose = verbose
        )
        super().__init__(
            hybridstore = hybridstore,
            llm = llm,
            primitives = primitives,
            plan_extractor = plan_extractor,
            primitive_executor = primitive_executor,
            primitive_executor_without_planning = primitive_executor_without_planning,
            user_language = user_language,
            user_expertise = user_expertise,
            max_depth = max_depth,
            max_breadth = max_breadth,
            max_plan_attempts = max_plan_attempts,
            similarity_threshold = similarity_threshold,
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
            print(f"{Fore.RED}{str(err)}{Style.RESET_ALL}")
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
        return len(self.plan_stack)

    def create_plan(self, objective:str) -> Optional[Graph]:
        """Method to create a plan"""
        plan = None
        attemps = 0
        thoughts = ""
        while plan is None:
            if attemps > self.max_plan_attempts:
                raise RuntimeError(f"Failing to plan after {attemps-1} attempts... Please verify/correct your prompts.")
            thinking_chain = LLMChain(llm=self.llm, prompt=TASK_PLANNER_THINKING_PROMPT.partial(
                self_description=HYBRID_AGI_SELF_DESCRIPTION,
                core_values=HYBRID_AGI_CORE_VALUES
                ), verbose=self.verbose)
            thoughts = thinking_chain.predict(input=objective, max_breadth=self.max_breadth)
            plan = self.plan_extractor.extract_graph(objective, PLAN_EXTRACTION_PROMPT.partial(thoughts=thoughts, example=PLAN_EXAMPLE_SMALL))
            attemps +=1
        vector = self.hybridstore.embedding_function(objective)
        metadata = {self.hybridstore.graph_key: plan.name}
        self.hybridstore.add_texts([thoughts], embeddings=[vector], metadatas=[metadata])
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

    def execute_task(self, task_name:str, task_purpose:str):
        """Method to execute a task."""
        context = self._get_context()
        result = ""
        # This try catch is ugly but works to fix langchain problem with mrkl agents
        # At least when it happen at the end of the execution.
        try:
            if self.get_current_depth() > self.max_depth:
                result = self.primitive_executor_without_planning.run(
                    task=task_name,
                    objective=self.shared_objective,
                    purpose=task_purpose,
                    context=context)
            else:
                result = self.primitive_executor.run(
                    task=task_name,
                    objective=self.shared_objective,
                    purpose=task_purpose,
                    context=context)
        except OutputParserException as err:
            pos = str(err).find("`")
            result = str(err)[pos+1:len(str(err))-2]
        task_summary = f"Task:\n{task_name}\nResult:\n{result}"
        self.completed_tasks.append(task_summary)
        return result

    def execute_plan(self, plan:Graph):
        """Execute a plan."""
        last_result = ""
        completed_independent_tasks = []
        completed_tasks = []
        # First we execute independent tasks
        query_result = plan.query('MATCH (n:Task) WHERE NOT (n)<-[:REQUIRES*]-() RETURN n')
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
            query = """MATCH (n:Task)-[:REQUIRES]->(m:Task) WHERE ALL (task IN $completed_task_names WHERE m.name = task) RETURN n"""
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
        # We start with a plan with only one task (to handle simple tasks without planning)
        self.shared_objective = objective
        plan = Graph(self.hybridstore.redis_key("plan"), self.hybridstore.client)
        self.hybridstore.metagraph.query('MERGE (n:Plan {name:"'+plan.name+'"})')
        plan.query('MERGE (n:Task {name:"'+objective+'", purpose:"'+objective+'"})')
        self.plan_stack.append(plan)
        final_result = self.execute_plan(plan)
        self.plan_stack.pop()
        return final_result