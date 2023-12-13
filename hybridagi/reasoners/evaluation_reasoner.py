"""The evaluation reasoner. Copyright (C) 2023 SynaLinks. License: GPL-3.0"""

from langchain.prompts import PromptTemplate
from .action_reasoner import ActionReasoner

EVALUATION_TEMPLATE = \
"""
{context}
Action Purpose: {purpose}
Action: {tool_name}
Action Input Prompt: {tool_prompt}
Action Input: {tool_input}

Evaluation: Please, evaluate the quality of the above Action Input
It is always better when less assumption are made.

Please ensure to use the following format to Answer:

Step 1: First reasoning step to evaluate the above Action Input
Step 2: Second reasoning step to evaluate the above Action Input
... and so on (max 5 reasoning steps)
Final Step (must be a score between 0.0 and 1.0):...

Please, always use the above format to answer"""

EVALUATION_PROMPT = PromptTemplate(
    input_variables = [
        "context",
        "purpose",
        "tool_name",
        "tool_prompt",
        "tool_input",
    ],
    template = EVALUATION_TEMPLATE,
)

class EvaluationReasoner(ActionReasoner):
    """LLM reasoner that can evaluate the quality of the tool's inferences"""
    max_evaluation_attemps: int = 5

    def get_evaluation_prompt_without_context(
            self,
            purpose: str,
            tool_name:str,
            tool_prompt: str,
            tool_input: str,
        ) -> str:
        """Returns the action prompt without context"""
        return EVALUATION_TEMPLATE.format(
            context = "",
            purpose = purpose,
            tool_name = tool_name,
            tool_prompt = tool_prompt,
            tool_input = tool_input,
        )

    def get_evaluation_context(
            self,
            purpose: str,
            tool_name: str,
            tool_prompt: str,
            tool_input: str,
        ) -> str:
        """Returns the evaluation context"""
        evaluation_prompt = self.get_evaluation_prompt_without_context(
            purpose = purpose,
            tool_name = tool_name,
            tool_prompt = tool_prompt,
            tool_input = tool_input,
        )
        context = self.trace_memory.get_context(
            evaluation_prompt,
            self.fast_llm_max_token,
        )
        return context

    def perform_evaluation(
            self,
            purpose: str,
            tool_name: str,
            tool_prompt: str,
            tool_input: str,
        ) -> str:
        """Method to perform an evaluation"""
        attemps = 0
        while attemps < self.max_evaluation_attemps:
            context = self.get_evaluation_context(
                purpose = purpose,
                tool_name = tool_name,
                tool_prompt = tool_prompt,
                tool_input = tool_input,
            )
            result = self.predict(
                prompt = EVALUATION_PROMPT,
                context = context,
                purpose = purpose,
                tool_name = tool_name,
                tool_prompt = tool_prompt,
                tool_input = tool_input,
            )
            if self.debug:
                print("Evaluation:" +result)
            evaluation = result.split()[-1].upper()
            evaluation = evaluation.strip(".")
            try:
                score = float(evaluation)
                break
            except Exception:
                pass
            attemps += 1
        try:
            score = float(evaluation)
        except Exception:
            raise ValueError(
                f"Failed to evaluate after {attemps} attemps."+
                f" Got {result} should finish with a score between 0.0 and 1.0,"+
                " please verify your prompts or programs.")
        return score

    async def async_perform_evaluation(
            self,
            purpose: str,
            tool_name: str,
            tool_prompt: str,
            tool_input: str,
        ) -> str:
        """Method to asynchronously perform an evaluation"""
        attemps = 0
        while attemps < self.max_evaluation_attemps:
            context = self.get_evaluation_context(
                purpose = purpose,
                tool_name = tool_name,
                tool_prompt = tool_prompt,
                tool_input = tool_input,
            )
            result = await self.async_predict(
                prompt = EVALUATION_PROMPT,
                context = context,
                purpose = purpose,
                tool_name = tool_name,
                tool_prompt = tool_prompt,
                tool_input = tool_input,
            )
            if self.debug:
                print("Evaluation:" +result)
            evaluation = result.split()[-1].upper()
            evaluation = evaluation.strip(".")
            try:
                score = float(evaluation)
                break
            except Exception:
                pass
            attemps += 1
        try:
            score = float(evaluation)
        except Exception:
            raise ValueError(
                f"Failed to evaluate after {attemps} attemps."+
                f" Got {result} should finish with a score between 0.0 and 1.0,"+
                " please verify your prompts or programs.")
        return score
