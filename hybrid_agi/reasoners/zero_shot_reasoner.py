
from typing import List
from pydantic import BaseModel
from langchain.base_language import BaseLanguageModel

from hybrid_agi.reasoners.base import BaseReasoner

class ZeroShotReasoner(BaseReasoner):
    llm: BaseLanguageModel

    def predict(self, prompt_template: str, **kwargs) -> str:
        return self.naive_predict(prompt_template, **kwargs)
    
    def decide(self, context: str, question: str, options: List[str]) -> str:
        return self.predict_decision(context, question, options,
            decision_prompt = ZERO_SHOT_PROMPTING_DECISION_PROMPT
        )

    def evaluate(self, context: str) -> float:
        return self.predict_evaluation(context,
            evaluation_prompt = ZERO_SHOT_PROMPTING_EVALUATION_PROMPT
        )