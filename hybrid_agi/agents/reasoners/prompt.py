
DECISION_TEMPLATE = \
"""
{context}

Imagine three different experts are answering this question.
All experts will write down 1 step of their thinking, then share it with the group.
Then all experts will go on to the next step, etc.
If any expert realises they're wrong at any point then they leave.
You MUST finish your Answer by {choice}.
The question is {question}
Answer:"""

DECISION_PROMPT = PromptTemplate(
    input_variables = ["context", "choice", "question"]
    template = DECISION_TEMPLATE
)

EVALUATION_TEMPLATE = \
"""
{context}

Imagine three different experts are evaluating the above response.
All experts will write down 1 step of their thinking, then share it with the group.
Then all experts will go on to the next step, etc.
If any expert realises they're wrong at any point then they leave.
You MUST finish your Answer by a float between 0.0 and 100.0 representing
the correctness and chances of success of the above response (0.0 means impossible).
The question is what are the chances of success of the above response?
Answer:"""

EVALUATION_PROMPT = PromptTemplate(
    input_variables = ["context", "question"],
    template = EVALUATION_TEMPLATE
)