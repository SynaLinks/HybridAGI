import dspy

class HelpfulInteractionSignature(dspy.Signature):
    """Check if the interaction is helpful"""
    context = dspy.InputField(desc="The context for the prediction")
    objective = dspy.InputField(desc="The objective")
    chat_history = dspy.InputField(desc="The chat history")
    helpful = dspy.OutputField(
        desc="Is the interaction helpful for the user?",
        prefix="Helpful[Yes/No]:",
    )

def helpful_interaction(example, prediction, trace=None):
    # This line means that we discard the example if the agent reached the max iterations
    # Meaning it was probably stuck in a loop
    if prediction.finish_reason == "max iters":
        return False
    # Check if the interaction is actually helpful
    pred = dspy.ChainOfThought(HelpfulInteractionSignature)(
        context=prediction.program_trace,
        objective=example.objective,
        chat_history=prediction.chat_history,
    )
    return pred.helpful.lower().strip().strip(".")=="yes"