"""The tree of thought reasoner. Copyright (C) 2023 SynaLinks. License: GPL-3.0"""

from typing import List
from pydantic import BaseModel
from langchain.base_language import BaseLanguageModel
from hybrid_agi.reasoners.base import BaseReasoner

from hybrid_agi.reasoners.prompt import (
    TREE_OF_THOUGHT_PROMPTING_DECISION_PROMPT,
    TREE_OF_THOUGHT_PROMPTING_EVALUATION_PROMPT,
    CHAIN_OF_THOUGHT_PROMPTING_DECISION_PROMPT,
    CHAIN_OF_THOUGHT_PROMPTING_EVALUATION_PROMPT
)

class TreeOfThoughtReasoner(BaseReasoner):
    llm: BaseLanguageModel
    n_prediction_proposals: int = 2
    n_select_sample: int = 2
    max_thinking_steps: int = 5
    success_threshold: float = 0.8
    pruning_threshold: float = 0.2
    verbose: bool = False

    def predict(self, prompt: str, **kwargs) -> str:
        """Method to predict the next words using Tree Of Thought technique"""
        # First we try to simply predict
        first_prediction = self.naive_predict(prompt, **kwargs)
        first_score = self.evaluate(prompt.format(**kwargs) + "\n" + first_prediction)
        if first_score > self.success_threshold:
            # If its good enought we stop here
            return first_prediction
        selected_proposals = [first_prediction]
        selected_proposals_score = [first_score]
        for n in range(0, self.max_thinking_steps-1):
            proposals = []
            proposals_scores = []
            for prediction in selected_proposals:
                for i in range (0, self.n_prediction_proposals):
                    proposal = self.naive_predict(prompt, **kwargs)
                    score = self.evaluate(
                        prompt.format(**kwargs)+prediction
                    )
                    if score >= self.success_threshold:
                        return proposal
                    if score > self.pruning_threshold:
                        proposals.append(proposal)
                        proposals_scores.append(score)
                    
            ids = range(0, len(proposals))
            # Greedy selection method
            selected_ids = \
            sorted(ids, key=lambda x: proposals_scores[x], reverse=True)[:self.n_select_sample]
            selected_proposals = [proposals[select_id] for select_id in selected_ids]
            selected_proposals_scores = \
            [proposals_scores[select_id] for select_id in selected_ids]
        return selected_proposals[0]

    def decide(self, context: str, question: str, options: List[str]) -> str:
        return self.predict_decision(context, question, options,
            decision_prompt = CHAIN_OF_THOUGHT_PROMPTING_DECISION_PROMPT
        )

    def evaluate(self, context: str) -> float:
        return self.predict_evaluation(context,
            evaluation_prompt = CHAIN_OF_THOUGHT_PROMPTING_EVALUATION_PROMPT
        )