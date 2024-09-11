# import dspy

# class FactualAnswerSignature(dspy.Signature):
#     """
#     Check if the answer is present in the provided trace
#     If the answer is not helpful to answer the objective question it means No
#     """
#     context = dspy.InputField(desc="The context for the prediction")
#     question = dspy.InputField(desc="Question to be answered")
#     answer = dspy.InputField(desc="Answer for the question")
#     correct = dspy.OutputField(
#         desc="Is the answer factually correct based on the context?",
#         prefix="Correct[Yes/No]:",
#     )
    
# class FactualAnswer(Metric):
    
#     def __init__(
#         lm: Optional[dspy.LM] = None,
#     ):
#         super().__init__(lm=lm)

#     def evaluate(example: Union[Query, QueryWithSession], prediction: AgentOutput, trace=None):
#         # This line means that we discard the example if the agent reached the max iterations
#         # Meaning it was probably stuck in a loop
#         if prediction.finish_reason == "max iters":
#             return False
#         # Check if the answer is actually based on the context
#         with dspy.context(lm=self.lm if self.lm is not None else dspy.settings.lm):
#             pred = dspy.ChainOfThought(FactualAnswerSignature)(
#                 context = prediction.program_trace,
#                 question = example.objective,
#                 answer = prediction.final_answer,
#             )
#         return pred.correct.lower().strip().strip(".")=="yes"