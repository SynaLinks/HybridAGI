import dspy
from pydantic import BaseModel

class CritiqueTrace(dspy.Signature):
    """Critique the trace based on the objective to assess"""
    objective = dspy.InputField(desc="The objective")
    trace = dspy.InputField(desc="The trace to assess")
    critique = dspy.OutputField(desc="The critique of the trace")

class Score(BaseModel):
    score: float

class CritiqueToScoreSignature(dspy.Signature):
    """Convert a critique into a score between 0.0 (bad) and 1.0 (good)"""
    critique = dspy.InputField(desc="The critique to convert into a score")
    score: Score = dspy.OutputField(desc="A score between 0.0 and 1.0")

def critique_trace(example, prediction, trace=None):
    # This line means that we discard the example if the agent reached the max iterations
    # Meaning it was probably stuck in a loop
    if prediction.finish_reason == "max iters":
        return False
    pred = dspy.ChainOfThought(CritiqueTrace)(
        objective = example.objective,
        trace = prediction.program_trace,
    )
    result = dspy.TypedPredictor(CritiqueToScoreSignature)(
        critique = pred.critique,
    )
    return result.score.score