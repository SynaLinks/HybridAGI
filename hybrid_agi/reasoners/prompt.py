from langchain.prompts.prompt import PromptTemplate

PREDICTION_TEMPLATE = \
"""
{context}
{instructions}
"""

PREDICTION_CHAIN_TEMPLATE = \
"""
{context}
{instructions}
{prediction}
{instructions}
"""

PREDICTION_PROMPT = PromptTemplate(
    input_variables = ["context", "instructions"],
    template = PREDICTION_TEMPLATE
)

PREDICTION_CHAIN_PROMPT = PromptTemplate(
    input_variables = ["context", "instructions", "prediction"],
    template = PREDICTION_CHAIN_TEMPLATE
)

ZERO_SHOT_PROMPTING_DECISION_TEMPLATE = \
"""
{context}

Please, you MUST finish your Answer by {choice}.
Question: {question}
Answer:"""

CHAIN_OF_THOUGHT_PROMPTING_DECISION_TEMPLATE = \
"""
{context}

Please, you MUST finish your Answer by {choice}.
Question: {question}
Answer: Let's think this out in a step by step way to be sure we have the right answer."""

TREE_OF_THOUGHT_PROMPTING_DECISION_TEMPLATE = \
"""
{context}

Imagine three different experts are answering this question.
All experts will write down 1 step of their thinking, then share it with the group.
Then all experts will go on to the next step, etc.
If any expert realises they're wrong at any point then they leave.
Please, you MUST finish your Answer by {choice}.
The question is {question}
Answer:"""

ZERO_SHOT_PROMPTING_DECISION_PROMPT = PromptTemplate(
    input_variables = ["context", "choice", "question"],
    template = ZERO_SHOT_PROMPTING_DECISION_TEMPLATE
)

CHAIN_OF_THOUGHT_PROMPTING_DECISION_PROMPT = PromptTemplate(
    input_variables = ["context", "choice", "question"],
    template = CHAIN_OF_THOUGHT_PROMPTING_DECISION_TEMPLATE
)

TREE_OF_THOUGHT_PROMPTING_DECISION_PROMPT = PromptTemplate(
    input_variables = ["context", "choice", "question"],
    template = TREE_OF_THOUGHT_PROMPTING_DECISION_TEMPLATE
)

ZERO_SHOT_PROMPTING_EVALUATION_TEMPLATE = \
"""
{context}

You MUST finish your Answer by a float between 0.0 and 100.0 representing
the correctness and chances of success of the above response (0.0 means impossible).
The question is what are the chances of success of the above response?
Answer:"""

CHAIN_OF_THOUGHT_PROMPTING_EVALUATION_TEMPLATE = \
"""
{context}

You MUST finish your Answer by a float between 0.0 and 100.0 representing
the correctness and chances of success of the above response (0.0 means impossible or none).
Question: What are the chances of the above response?
Answer: \
Let's think this out in a step by step way to be sure we have the right answer."""

TREE_OF_THOUGHT_PROMPTING_EVALUATION_TEMPLATE = \
"""
{context}

Imagine three different experts are evaluating the above response.
All experts will write down 1 step of their thinking, then share it with the group.
Then all experts will go on to the next step, etc.
If any expert realises they're wrong at any point then they leave.
You MUST finish your Answer by a float between 0.0 and 100.0 representing
the correctness and chances of success of the above response (0.0 means impossible or none).
Question: What are the chances of the above response?
Answer:"""

ZERO_SHOT_PROMPTING_EVALUATION_PROMPT = PromptTemplate(
    input_variables = ["context"],
    template = ZERO_SHOT_PROMPTING_EVALUATION_TEMPLATE
)

CHAIN_OF_THOUGHT_PROMPTING_EVALUATION_PROMPT = PromptTemplate(
    input_variables = ["context"],
    template = CHAIN_OF_THOUGHT_PROMPTING_EVALUATION_TEMPLATE
)

TREE_OF_THOUGHT_PROMPTING_EVALUATION_PROMPT = PromptTemplate(
    input_variables = ["context"],
    template = TREE_OF_THOUGHT_PROMPTING_EVALUATION_TEMPLATE
)