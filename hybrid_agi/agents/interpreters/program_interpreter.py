"""The graph program interpreter. Copyright (C) 2023 SynaLinks. License: GPL-3.0"""

from collections import deque
from typing import List, Optional, Iterable
from pydantic import BaseModel, Extra
from colorama import Fore, Style
from redisgraph import Node, Graph 
from collections import OrderedDict

from langchain.chains.llm import LLMChain
from langchain.tools import Tool
from langchain.base_language import BaseLanguageModel
from hybrid_agi.hybridstores.redisgraph import RedisGraphHybridStore
from langchain.prompts.prompt import PromptTemplate

EVALUATION = \
"""
Evaluation Purpose: Evaluate the relevance of the answer to refine it if needed
Evaluation Question: 
You are an expert in evaluating the relevance of answers
Please evaluate the chances of success of this response by a float between 0.0 and 100.0
Remove any additionnal comment
Evaluation Answer (MUST be between 0.0 and 100.0):"""

REFINEMENT = \
"""
You are an very smart expert in improving things.
If things can be improved, please incorporate the improvements.
"""

class GraphProgramInterpreter(BaseModel):
    """LLM based interpreter for graph programs"""
    hybridstore: RedisGraphHybridStore
    llm: BaseLanguageModel
    program_key: str
    prompt: str = ""
    default_prompt: str = ""
    final_prompt: str = ""
    monitoring_prompt: str = ""
    prompt_deque: Iterable = deque()
    program_stack: Iterable = deque()
    max_iteration: int = 50
    max_decision_attemps: int = 5
    max_token: int = 4000
    allowed_tools: List[str] = []
    tools_map: OrderedDict[str, Tool] = {}
    language: str = "English"
    tools_instructions: str = ""
    monitoring: bool = True
    n_prediction_proposals: int = 2
    n_select_sample: int = 2
    max_thinking_steps: int = 5
    success_threshold: float = 80.0
    evaluation_prompt: str = ""
    verbose: bool = True

    class Config:
        """Configuration for this pydantic object."""
        extra = Extra.forbid
        arbitrary_types_allowed = True

    def __init__(
            self,
            hybridstore: RedisGraphHybridStore,
            llm: BaseLanguageModel,
            program_key:str = "",
            prompt:str = "",
            monitoring_prompt:str = "",
            final_prompt:str = "",
            tools:List[Tool] = [],
            max_iteration: int = 50,
            max_decision_attemps: int = 5,
            max_token:int = 4000,
            language: str = "English",
            monitoring: bool = True,
            n_prediction_proposals: int = 3,
            n_select_sample: int = 2,
            max_thinking_steps: int = 5,
            success_threshold: float = 90.0,
            evaluation_prompt: str = "",
            verbose: bool = True
        ):
        if program_key == "":
            program_key = hybridstore.main.name
        final_prompt = final_prompt if final_prompt else "The final answer in {language}.\nFinal Answer:"
        monitoring_prompt = monitoring_prompt if monitoring_prompt else "Critisize the above Action and show your work. Without additionnal information.\nCritique:"
        super().__init__(
            hybridstore = hybridstore,
            llm = llm,
            program_key = program_key,
            prompt = prompt,
            monitoring_prompt = monitoring_prompt,
            final_prompt = final_prompt,
            default_prompt = prompt,
            max_iteration = max_iteration,
            max_decision_attemps = max_decision_attemps,
            max_token = max_token,
            language = language,
            monitoring = monitoring,
            n_prediction_proposals = 3,
            n_select_sample = 2,
            max_thinking_steps = 5,
            success_threshold = 90.0,
            verbose = verbose
        )
        self.tools_instructions = "You have access to the following tools:\n"
        for tool in tools:
            self.tools_instructions += f"\n{tool.name}:{tool.description}"
            self.allowed_tools.append(tool.name)
            self.tools_map[tool.name] = tool
        self.prompt += "\n" +self.tools_instructions

    def get_current_program(self) -> Optional[Graph]:
        """Method to retreive the current plan from the stack"""
        if len(self.program_stack) > 0:
            return self.program_stack[len(self.program_stack)-1]
        return None

    def get_next(self, node:Node) -> Optional[Node]:
        """Method to get the next node"""
        name = node.properties["name"]
        result = self.get_current_program().query('MATCH ({name:"'+name+'"})-[:NEXT]->(n) RETURN n')
        if len(result.result_set) > 0:
            return result.result_set[0][0]
        return None

    def predict(self, prompt:str) -> str:
        """Predict the next words using the context"""
        prediction_prompt = (self.prompt+"\n"+prompt)[:self.max_token]
        prompt_template = PromptTemplate.from_template(prediction_prompt)
        chain = LLMChain(llm=self.llm, prompt=prompt_template, verbose=False)
        prediction = chain.predict(language=self.language)
        pos = prediction.find("Action:")
        if pos> 0:
            prediction = prediction[:pos]
        return prediction

    def tree_of_thought(self, prompt:str) -> str:
        """Enhance the prediction using tree of thought technique"""
        # First we try to simply predict
        first_prediction = self.predict(prompt)
        eval_value = self.predict(prompt + first_prediction + EVALUATION)
        selected = [first_prediction]
        values = [float(eval_value.strip())]
        # If its good enought we stop here
        if max(values) > self.success_threshold:
            return first_prediction
        for n in range(0, self.max_thinking_steps):
            proposals = []
            values = []
            for prediction in selected:
                for i in range (0, self.n_prediction_proposals):
                    refinement_prompt = prompt.replace("Action Input:", f"Action Input: {REFINEMENT}")
                    proposal = self.predict(prompt + prediction + refinement_prompt)
                    proposals.append(proposal)
                    # print(f"Proposal {i}: \n{proposal}")
                    eval_value = self.predict(prompt + prediction + EVALUATION)
                    values.append(float(eval_value.strip()))
                    # print(f"Proposal {i} Score: \n{eval_value}")
            ids = range(0, len(proposals))
            # Greedy selection method
            selected_ids = sorted(ids, key=lambda x: values[x], reverse=True)[:self.n_select_sample]
            selected = [proposals[select_id] for select_id in selected_ids]
            values = [values[select_id] for select_id in selected_ids]
            # print(f"Selected proposals: {selected}")
            if max(values) > self.success_threshold:
                break
        # print(f"Final answer: {selected[0]}")
        return selected[0]

    def execute_program(self, program_index:str):
        """Method to execute a program"""
        program = Graph(program_index, self.hybridstore.client)
        self.program_stack.append(program)
        result = self.get_current_program().query('MATCH (n:Control {name:"Start"}) RETURN n')
        if len(result.result_set) == 0:
            raise ValueError("No entry point in the program")
        if len(result.result_set) > 1:
            raise ValueError("Multiple entry point in the program")
        starting_node = result.result_set[0][0]
        current_node = self.get_next(starting_node)
        next_node = None
        iteration = 0
        while True:
            if current_node.label == "Program":
                self.call_program(current_node)
                next_node = self.get_next(current_node)
            elif current_node.label == "Action":
                self.use_tool(current_node)
                next_node = self.get_next(current_node)
                if self.monitoring:
                    self.monitor()
            elif current_node.label == "Decision":
                next_node = self.decide_next(current_node)
            elif current_node.label == "Control":
                if current_node.properties["name"] == "End":
                    break
            else:
                raise RuntimeError("Invalid label for node. Please verify your programs using RedisInsight.")
            if next_node is None:
                raise RuntimeError("Program failed after reaching a non-terminated path. Please verify your programs using RedisInsight.")
            current_node = next_node
            iteration += 1
            if iteration > self.max_iteration:
                raise RuntimeError("Program failed after reaching max iteration")
        self.program_stack.pop()

    def decide_next(self, node:Node) -> Node:
        """Method to make a decision"""
        # get possible output options
        purpose = node.properties["name"]
        question = node.properties["question"]
        prompt = f"Decision: {question}.\nDecision Purpose: {purpose}.\n"
        outcomes = []
        result = self.get_current_program().query('MATCH (n:Decision {name:"'+purpose+'"})-[r]->() RETURN type(r)')
        for record in result.result_set:
            outcomes.append(record[0])
        choice = " or ".join(outcomes)
        prompt += f"Decision Answer (must be {choice}): "
        decision = ""
        attemps = 0
        while True:
            decision = self.predict(prompt).strip()
            decision = decision.upper()
            attemps += 1
            if decision in outcomes:
                break
            if attemps > self.max_decision_attemps:
                raise ValueError(f"Failed to decide after {attemps-1} attemps (Last Decision: '{decision}' should be {choice}). Please verify your programs.")
        prompt += decision
        self.update(prompt)
        result = self.get_current_program().query('MATCH (:Decision {name:"'+purpose+'"})-[:'+decision+']->(n) RETURN n')
        next_node = result.result_set[0][0]
        return next_node

    def use_tool(self, node:Node):
        """Method to use a tool"""
        purpose = node.properties["name"]
        tool_name = node.properties["tool"]
        tool_params_prompt = node.properties["params"]
        tool_prompt = f"Action: {tool_name}\nAction Purpose: {purpose}\nAction Input: {tool_params_prompt}"
        if tool_name == "Predict":
            tool_input = tool_params_prompt
            observation = self.tree_of_thought(tool_prompt)
            final_prompt = f"Action: {tool_name}\nAction Purpose: {purpose}\nAction Input: {tool_input}\n{observation}"
        else:
            tool_input = self.predict(tool_prompt)
            observation = self.execute_tool(tool_name, tool_input)
            final_prompt = f"Action: {tool_name}\nAction Purpose: {purpose}\nAction Input: {tool_input}\nAction Observation: {observation}"
        self.update(final_prompt)

    def call_program(self, node:Node):
        """Method to use a sub-program"""
        purpose = node.properties["name"]
        program = node.properties["program"]
        self.update(f"Start SubProgram: {program}\nSubProgram Purpose: {purpose}")
        self.execute_program(program)
        self.update(f"End SubProgram: {program}")

    def execute_tool(self, name:str, query:str):
        """Method to run the given tool"""
        if name not in self.allowed_tools:
            raise ValueError(f"Tool '{name}' not allowed. Please use another one.")
        if name not in self.tools_map:
            raise ValueError(f"Tool '{name}' not registered. Please use another one.")
        try:
            return self.tools_map[name].run(query)
        except Exception as err:
            return str(err)

    def update(self, prompt:str):
        """Method to update the program prompt"""
        if self.verbose:
            if prompt.startswith("Action"):
                print(f"{Fore.MAGENTA}{prompt}{Style.RESET_ALL}")
            elif prompt.startswith("Decision"):
                print(f"{Fore.BLUE}{prompt}{Style.RESET_ALL}")
            elif prompt.startswith("Critique"):
                print(f"{Fore.RED}{prompt}{Style.RESET_ALL}")
            else:
                print(f"{Fore.GREEN}{prompt}{Style.RESET_ALL}")
        while self.llm.get_num_tokens(self.prompt + "\n" + prompt) > self.max_token:
            self.clear()
            self.prompt += "\n".join(self.prompt_deque.pop())
        self.prompt += "\n" + prompt
        self.prompt_deque.appendleft(prompt)

    def monitor(self):
        """Method to monitor the process"""
        critique = self.predict(self.monitoring_prompt)
        self.update(f"Critique: {critique}")

    def clear(self):
        """Method to clear the prompt"""
        self.prompt = self.default_prompt + "\n" + self.tools_instructions

    def run(self, objective:str):
        """Method to run the agent"""
        self.clear()
        self.prompt += "\n"+f"The Objective is from the perspective of the User.\nObjective: {objective}"
        print(f"{Fore.GREEN}{self.prompt}{Style.RESET_ALL}")
        self.execute_program(self.program_key)
        result = self.predict(self.final_prompt)
        return result