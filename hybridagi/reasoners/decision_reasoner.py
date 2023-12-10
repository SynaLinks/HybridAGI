import asyncio
from typing import List, Optional, Callable
from langchain.prompts import PromptTemplate
from .base import BaseReasoner

DECISION_TEMPLATE = \
"""{context}
Decision Purpose: {purpose}
Decision: {question}

Please ensure to use the following format to Answer:

Step 1: First reasoning step to answer to the Decision
Step 2: Second reasoning step to answer to the Decision
... and so on (max 5 reasoning steps)
Final Step (must be {choice}):...

Please, always use the above format to answer"""

DECISION_PROMPT = PromptTemplate(
    input_variables = ["context", "purpose", "question", "choice"],
    template = DECISION_TEMPLATE
)

class DecisionReasoner(BaseReasoner):
    """LLM reasoner that can make explicit decision"""
    max_decision_attemps: int = 5

    pre_decision_callback: Optional[
        Callable[
            [str, str, List[str]],
            None
        ]
    ] = None
    post_decision_callback: Optional[
        Callable[
            [str, str, List[str], str],
            None
        ]
    ] = None

    def get_decision_prompt_without_context(
            self,
            purpose: str,
            question: str,
            choice: str,
        ) -> str:
        """Returns the decision prompt without context"""
        return DECISION_TEMPLATE.format(
            context = "",
            purpose = purpose,
            question = question,
            choice = choice)

    def get_decision_context(
            self,
            purpose: str,
            question: str,
            choice: str,
        ) -> str:
        """Returns the decision context"""
        decision_prompt = self.get_decision_prompt_without_context(
            purpose = purpose,
            question = question,
            choice = choice,
        )
        context = self.trace_memory.get_context(
            decision_prompt,
            self.fast_llm_max_token,
        )
        return context

    def perform_decision(
            self,
            purpose:str, 
            question: str,
            options: List[str]
        ) -> str:
        """Method to perform a decision"""
        if self.pre_decision_callback is not None:
            self.pre_decision_callback(
                purpose,
                question,
                options,
            )
        choice = " or ".join(options)
        attemps = 0
        while attemps < self.max_decision_attemps:
            context = self.get_decision_context(
                purpose = purpose,
                question = question,
                choice = choice, 
            )
            result = self.predict(
                prompt = DECISION_PROMPT,
                context = context,
                purpose = purpose,
                question = question,
                choice = choice,
            )
            if self.debug:
                print("Decision:" +result)
            decision = result.split()[-1].upper()
            decision = decision.strip(".")
            if decision in options:
                break
            attemps += 1
        if decision not in options:
            raise ValueError(
                f"Failed to decide after {attemps} attemps."+
                f" Got {result} should finish with {choice},"+
                " please verify your prompts or programs.")
        if self.post_decision_callback is not None:
            self.post_decision_callback(
                purpose,
                question,
                options,
                decision,
            )
        return decision

    async def async_perform_decision(
            self,
            purpose:str, 
            question: str,
            options: List[str]
        ) -> str:
        """Method to perform a decision"""
        if self.pre_decision_callback is not None:
            asyncio.create_task(
                self.pre_decision_callback(
                    purpose,
                    question,
                    options,
                )
            )
        choice = " or ".join(options)
        attemps = 0
        while attemps < self.max_decision_attemps:
            context = self.get_decision_context(
                purpose = purpose,
                question = question,
                choice = choice, 
            )
            result = await self.async_predict(
                prompt = DECISION_PROMPT,
                context = context,
                purpose = purpose,
                question = question,
                choice = choice,
            )
            if self.debug:
                print("Decision:" +result)
            decision = result.split()[-1].upper()
            decision = decision.strip(".")
            if decision in options:
                break
            attemps += 1
        if decision not in options:
            raise ValueError(
                f"Failed to decide after {attemps} attemps."+
                f" Got {result} should finish with {choice},"+
                " please verify your prompts or programs.")
        if self.post_decision_callback is not None:
            asyncio.create_task(
                self.post_decision_callback(
                    purpose,
                    question,
                    options,
                    decision,
                )
            )
        return decision
