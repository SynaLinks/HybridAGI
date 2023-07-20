"""The tree of thought tool. Copyright (C) 2023 SynaLinks. License: GPL-3.0"""

from colorama import Fore
from colorama import Style
from typing import Optional, List
from langchain.callbacks.manager import AsyncCallbackManagerForToolRun, CallbackManagerForToolRun
from langchain.tools import BaseTool, StructuredTool, Tool, tool
from langchain.prompts.prompt import PromptTemplate
from langchain.chains.llm import LLMChain

PROPOSALS_TEMPLATE = \
"""Please Answer the following Question without providing additionnal information.
If any enhancement can be made, incorporate them.
Let's think this out in a step by step way to be sure we have the right answer.
Question: {question}
Intermediate Answer: {intermediate_answer}
Answer:"""

PROPOSALS_PROMPT = PromptTemplate(
    input_variables = ["question", "intermediate_answer"],
    template = PROPOSALS_TEMPLATE
)

VOTES_TEMPLATE = \
"""
Please evaluate the following Answer. Let's think this out in a step by step way to be sure we have the right evaluation.
Your Evaluation should be a float between 0.0 and 100.0 representing the chances of success of the Answer (0.0 means no chance).
Question: {question}
Answer: {answer}
Evaluation:"""

VOTES_PROMPT = PromptTemplate(
    input_variables = ["question", "answer"],
    template = VOTES_TEMPLATE
)

class TreeOfThoughtTool(BaseTool):
    name = "TreeOfThought"
    description = \
    """
    Usefull to provide better answer for logical thinking or coding.
    """
    n_proposals: int = 3
    n_select_sample: int = 2
    max_steps: int = 5
    success_threshold = 95.0

    def _run(self, query:str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        """Use the tool."""
        selected = [""]
        for n in range(0, self.max_steps):
            # Generate proposals
            proposals = [self.get_proposals(query, answer) for answer in selected]
            # Evaluate them
            values = self.get_values(query, proposals)
            # Select the best ones (greedy method)
            selected_ids = sorted(ids, key=lambda x: values[x], reverse=True)[:self.n_select_sample]
            selected = [proposals[select_id] for select_id in selected_ids]
            if max(values) > self.success_threshold:
                break
        return selected[0]

    async def _arun(self, query: str,  run_manager: Optional[AsyncCallbackManagerForToolRun] = None) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("TreeOfThought does not support async")

    def get_proposals(self, question:str, intermediate_answer:str) -> List[str]:
        proposals = []
        for n in range(0, self.n_proposals):
            chain = LLMChain(llm=self.llm, prompt=PROPOSALS_PROMPT)
            answer = chain.predict(question=question, intermediate_answer=intermediate_answer)
            proposals.append(answer)
        return proposals

    def get_values(self, question:str, proposals: List[str]) -> List[float]:
        votes = []
        for answer in proposals:
            chain = LLMChain(llm=self.llm, prompt=VOTES_PROMPT)
            eval_str = chain.predict(question=question, answer=answer)
            score = float(eval_str.strip())
            votes.append(score)
        return votes