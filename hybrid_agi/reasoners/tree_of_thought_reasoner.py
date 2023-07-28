"""The tree of thought reasoner. Copyright (C) 2023 SynaLinks. License: GPL-3.0"""

from typing import List
from langchain.base_language import BaseLanguageModel

class TreeOfThoughtReasoner(BaseModel):
    llm: BaseLanguageModel
    n_prediction_proposals: int = 2
    n_select_sample: int = 2
    max_thinking_steps: int = 5
    success_threshold: float = 90.0
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
        for i in range (0, self.n_prediction_proposals-1):
            prediction = self.naive_predict(prompt, **kwargs)
            score = self.evaluate(prompt.format(**kwargs) + "\n" + prediction)
            selected_proposals.append(prediction)
            selected_proposals_scores.append(score)
            if score > self.success_threshold:
                return prediction
        for n in range(0, self.max_thinking_steps-1):
            proposals = []
            proposals_scores = []
            for prediction in selected_proposals:
                for i in range (0, self.n_prediction_proposals):
                    proposal = self.naive_predict(
                        prompt+"\n"+prediction+"\n"+prompt
                    )
                    score = self.self.evaluate(
                        prompt.format(**kwargs)+"\n"+prediction
                    )
                    if score > self.success_threshold:
                        return prediction
                    proposals.append(proposal)
                    proposals_scores.append(score)
            ids = range(0, len(proposals))
            # Greedy selection method
            selected_ids = \
            sorted(ids, key=lambda x: values[x], reverse=True)[:self.n_select_sample]
            selected_proposals = [proposals[select_id] for select_id in selected_ids]
            selected_proposals_scores = \
            [proposals_values[select_id] for select_id in selected_ids]
        return selected[0]

    def decide(self, context: str, question: str, options: List[str]) -> str:
        return self.predict_decision(context, question, options,
            decision_prompt = TREE_OF_THOUGHT_PROMPTING_DECISION_PROMPT
        )

    def evaluate(self, context: str) -> float:
        return self.predict_evaluation(context,
            evaluation_prompt = TREE_OF_THOUGHT_PROMPTING_EVALUATION_PROMPT
        )