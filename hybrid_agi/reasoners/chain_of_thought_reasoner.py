"""The chain of thought reasoner. Copyright (C) 2023 SynaLinks. License: GPL-3.0"""

from typing import List
from pydantic import BaseModel
from langchain.base_language import BaseLanguageModel
from hybrid_agi.reasoners.base import BaseReasoner

from hybrid_agi.reasoners.prompt import (
    TREE_OF_THOUGHT_PROMPTING_DECISION_PROMPT,
    TREE_OF_THOUGHT_PROMPTING_EVALUATION_PROMPT
)

class ChainOfThoughtReasoner(BaseReasoner):
    llm: BaseLanguageModel
    max_thinking_steps: int = 5
    success_threshold: float = 80.0
    verbose: bool = False

    def predict(self, prompt: str, **kwargs) -> str:
        selected_proposal = ""
        selected_proposal_score = 0.0
        for i in range(0, self.max_thinking_steps):
            if not selected_proposal:
                prediction = self.naive_predict(prompt, **kwargs)
            else:
                prediction = self.naive_predict(prompt+selected_proposal+prompt, **kwargs)
            score = self.evaluate(prompt.format(**kwargs) + "\n" + prediction)
            if score > self.success_threshold:
                break
        return selected_proposal

    def predict(self, prompt_template: str, **kwargs) -> str:
        prompt = PromptTemplate.from_template(prompt_template)
        chain = LLMChain(llm=self.llm, prompt=prompt, verbose=self.verbose)
        prediction = chain.predict(**kwargs)
        return prediction

    def decide(self, context: str, question: str, options: List[str]) -> str:
        return self.predict_decision(context, question, options,
            decision_prompt = CHAIN_OF_THOUGHT_PROMPTING_DECISION_PROMPT
        )

    def evaluate(self, context: str) -> float:
        return self.predict_evaluation(context,
            evaluation_prompt = CHAIN_OF_THOUGHT_PROMPTING_EVALUATION_PROMPT
        )