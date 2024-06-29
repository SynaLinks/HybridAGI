import dspy

class FactualAnswerSignature(dspy.Signature):
    """Check if the answer is present in the provided trace"""
    context = dspy.InputField(desc="The context for the prediction")
    question = dspy.InputField(desc="Question to be answered")
    answer = dspy.InputField(desc="Answer for the question")
    correct = dspy.OutputField(
        desc="Is the answer factually correct based on the context?",
        prefix="Correct[Yes/No]:",
    )

def factual_answer(example, prediction, trace=None):
    # This line means that we discard the example if the agent reached the max iterations
    # Meaning it was probably stuck in a loop
    if prediction.finish_reason == "max iters":
        return False
    # Check if the answer is actually based on the context
    pred = dspy.ChainOfThought(FactualAnswerSignature)(
        context = prediction.program_trace,
        question = example.objective,
        answer = prediction.final_answer,
    )
    return pred.correct.lower().strip().strip(".")=="yes"