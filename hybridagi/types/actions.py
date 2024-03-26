import dspy
import json
from typing import List, Optional

ACTION_TEMPLATE = \
""" --- Step {hop} ---
Action Purpose: {purpose}
Action: {prediction}"""

DECISION_TEMPLATE = \
""" --- Step {hop} ---
Decision Purpose: {purpose}
Decision Question: {question}
Decision: {answer}"""

CALL_PROGRAM_TEMPLATE = \
""" --- Step {hop} ---
Call Program: {program}
Program Purpose: {purpose}"""

END_PROGRAM_TEMPLATE = \
""" --- Step {hop} ---
End Program: {program}"""

class AgentAction():
    hop: int
    purpose: str
    tool: str
    prompt: str = ""
    log: str = ""

    def __init__(
            self,
            hop: int,
            purpose: str,
            tool: str,
            prompt: str = "",
            prediction: Optional[dspy.Prediction] = None,
            log: str = "",
        ):
        self.hop = hop
        self.purpose = purpose
        self.tool = tool
        self.prompt = prompt
        self.prediction = prediction
        self.log = log

    def __str__(self):
        return ACTION_TEMPLATE.format(
            hop = self.hop,
            purpose = self.purpose,
            prediction = json.dumps(dict(self.prediction), indent=2) if self.prediction else "None",
        )

class AgentDecision():
    hop: int
    purpose: str
    question: str
    options: List[str]
    answer: str
    log: str = ""

    def __init__(
            self,
            hop: int,
            purpose: str,
            question: str,
            options: List[str],
            answer: str,
            prompt: str = "",
            log: str = "",
        ):
        self.hop = hop
        self.purpose = purpose
        self.question = question
        self.options = options
        self.prompt = prompt
        self.answer = answer
        self.log = log

    def __str__(self):
        return DECISION_TEMPLATE.format(
            hop = self.hop,
            purpose = self.purpose,
            question = self.question,
            answer = self.answer,
        )

class ProgramCall():
    hop: int
    purpose: str
    program: str

    def __init__(
            self,
            hop: int,
            purpose: str,
            program: str,
        ):
        self.hop = hop
        self.purpose = purpose
        self.program = program

    def __str__(self):
        return CALL_PROGRAM_TEMPLATE.format(
            hop = self.hop,
            purpose = self.purpose,
            program = self.program,
        )

class ProgramEnd():
    hop: int
    program: str

    def __init__(
            self,
            hop: int,
            program: str,
        ):
        self.hop = hop
        self.program = program

    def __str__(self):
        return END_PROGRAM_TEMPLATE.format(
            hop = self.hop,
            program = self.program,
        )