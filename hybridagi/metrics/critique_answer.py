import dspy
from pydantic import BaseModel

class CritiqueAnswer(dspy.Signature):
    """Critique the answer of the the question"""
    question = dspy.InputField(desc="The question")
    answer = dspy.InputField(desc="The answer to assess")
    critique = dspy.OutputField(desc="The critique of the answer")

class Score(BaseModel):
    score: float

class CritiqueToScoreSignature(dspy.Signature):
    """Convert a critique into a score between 0.0 (bad) and 1.0 (good)"""
    critique = dspy.InputField(desc="The critique to convert into a score")
    score: Score = dspy.OutputField(desc="A score between 0.0 and 1.0")

def critique_answer(example, prediction, trace=None):
    # This line means that we discard the example if the agent reached the max iterations
    # Meaning it was probably stuck in a loop
    if prediction.finish_reason == "max iters":
        return False
    pred = dspy.ChainOfThought(CritiqueAnswer)(
        question = example.objective,
        answer = prediction.final_answer,
    )
    result = dspy.TypedPredictor(CritiqueToScoreSignature)(
        critique = pred.critique,
    )
    return result.score.score