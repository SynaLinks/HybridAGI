"""The decision reasoner. Copyright (C) 2023 SynaLinks. License: GPL-3.0"""

import asyncio
from typing import List

from .decision_reasoner import DecisionReasoner, DECISION_PROMPT

class VoteDecisionReasoner(DecisionReasoner):

    def perform_decision(
            self,
            purpose:str,
            question: str,
            options: List[str],
            nb_vote: int = 5,
        ) -> str:
        """Method to perform a decision"""
        if self.pre_decision_callback is not None:
            self.pre_decision_callback(
                purpose,
                question,
                options,
            )
        choice = " or ".join(options)
        results = {o:0 for o in options}

        def get_prediction():
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
                results[decision] += 1

        for _ in range(nb_vote):
            get_prediction()

        results_scores = zip(results.keys(), results.values())
        sorted_results = sorted(
            results_scores,
            key=lambda x: x[1],
            reverse=True)
        best_decision, _ = sorted_results[0]
        decision = best_decision
        self.trace_memory.commit_decision(
            purpose = purpose,
            question = question,
            options = options,
            decision = decision,
        )
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
            options: List[str],
            nb_vote: int = 5,
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
        results = {o:0 for o in options}

        async def get_prediction():
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
                results[decision] += 1
        
        tasks = [get_prediction() for _ in range(nb_vote)]
        await asyncio.gather(*tasks)

        results_scores = zip(results.keys(), results.values())
        sorted_results = sorted(
            results_scores,
            key=lambda x: x[1],
            reverse=True)
        best_decision, _ = sorted_results[0]
        decision = best_decision
        
        self.trace_memory.commit_decision(
            purpose = purpose,
            question = question,
            options = options,
            decision = decision,
        )
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
