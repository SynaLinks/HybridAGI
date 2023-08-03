import abc
from typing import List, Any
from pydantic import BaseModel
from langchain.chains.llm import LLMChain
from langchain.prompts.prompt import PromptTemplate

from hybrid_agi.reasoners.prompt import(
    ZERO_SHOT_PROMPTING_DECISION_PROMPT,
    ZERO_SHOT_PROMPTING_EVALUATION_PROMPT
)

class BaseReasoner(BaseModel):
    max_decision_attemps: int = 5

    @abc.abstractmethod
    def predict(self, context: str, prompt: str, **kwargs) -> str:
        pass

    @abc.abstractmethod
    def decide(self, context: str, question: str, options: List[str]) -> str:
        pass

    @abc.abstractmethod
    def evaluate(self, context: str) -> float:
        pass

    def naive_predict(self, prompt_template: str, **kwargs) -> str:
        prompt = PromptTemplate.from_template(prompt_template)
        chain = LLMChain(llm=self.llm, prompt=prompt, verbose=True)
        prediction = chain.predict(**kwargs)
        return prediction
    
    def predict_decision(
            self,
            context: str,
            question: str,
            options: List[str],
            decision_prompt: PromptTemplate = None,
            **kwargs : Any
        ) -> str:
        """Method to decide using a LLM"""
        if decision_prompt is None:
            decision_prompt = ZERO_SHOT_PROMPTING_DECISION_PROMPT
        chain = LLMChain(llm=self.llm, prompt=decision_prompt, verbose=True)
        
        choice = " or ".join(options)
        attemps = 0
        while attemps < self.max_decision_attemps:
            result = chain.predict(
                context=context,
                question=question,
                choice=choice,
                **kwargs)
            print(result)
            decision = result.split()[-1].upper()
            decision = decision.strip(".")
            if decision in options:
                break
            attemps += 1
        if decision not in options:
            raise ValueError(
                f"Failed to decide after {attemps} attemps."+
                f" Got {decision} should be {choice},"+
                " please verify your prompts or programs."
            )
        return decision

    def predict_evaluation(
            self,
            context: str,
            evaluation_prompt: PromptTemplate = None,
            **kwargs : Any
        ) -> float:
        """Method to evaluate using a LLM"""
        if evaluation_prompt is None:
            evaluation_prompt = ZERO_SHOT_PROMPTING_EVALUATION_PROMPT
        chain = LLMChain(llm=self.llm, prompt=evaluation_prompt, verbose=True)
        attemps = 0
        score = None
        while attemps < self.max_decision_attemps:
            result = chain.predict(context=context, **kwargs)
            print(result)
            if len(result.split()) > 0:
                evaluation = result.split()[-1]
                evaluation = evaluation.strip(".")
            else:
                evaluation = None
            try:
                score = float(evaluation)
                break
            except:
                pass
            attemps += 1
        if score is None:
            raise ValueError(
                f"Failed to evaluate after {attemps} attemps."+
                f" Got {evaluation}, should be a float between 0.0 and 100.0,"+
                " please verify your prompts or programs."
            )
        return score