"""The tree of thought reasoner. Copyright (C) 2023 SynaLinks. License: GPL-3.0"""

from typing import List
from langchain.base_language import BaseLanguageModel

class TreeOfThoughtReasoner(BaseModel):
    llm: BaseLanguageModel
    n_prediction_proposals: int = 2
    n_select_sample: int = 2
    max_thinking_steps: int = 5
    success_threshold: float = 80.0
    verbose: bool = False
    naive_mode: bool = False

    def naive_predict(self, prompt:str, **kwargs) -> str:
        """Method to predict the next words"""
        prompt_template = PromptTemplate.from_template(prompt)
        chain = LLMChain(llm=self.llm, prompt=prompt_template, verbose=self.verbose)
        prediction = chain.predict(**kwargs)
        return prediction

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
        """Method to decide using Tree Of Thought Prompting technique"""
        chain = LLMChain(llm=self.llm, prompt=DECISION_PROMPT, verbose=False)
        choice = " or ".join(options)
        attemps = 0
        while attemps < self.max_decision_attemps:
            result = chain.predict(context=context, question=question, choice=choice)
            decision = result.strip()[-1]
            if decision in options:
                break
            attemps += 1
        if decision not in options:
            raise ValueError(
                f"Failed to decide after {attemps-1} attemps."+
                " Please verify your prompts."
            )
        return decision

    def evaluate(self, context: str) -> float:
        """Method to evaluate using Tree Of Thought Prompting technique"""
        chain = LLMChain(llm=self.llm, prompt=EVALUATION_PROMPT, verbose=False)
        choice = " or ".join(options)
        attemps = 0
        score = None
        while attemps < self.max_decision_attemps:
            result = chain.predict(context=context)
            evaluation = result.strip()[-1]
            try:
                score = float(evaluation)
                break
            except:
                pass
            attemps += 1
        if score is None:
            raise ValueError(
                f"Failed to evaluate after {attemps-1} attemps."+
                " Please verify your prompts."
            )
        return score