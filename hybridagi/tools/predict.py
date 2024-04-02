import dspy
from .base import BaseTool

class PredictSignature(dspy.Signature):
    """Infer the best answer according to the provided instructions"""
    objective = dspy.InputField(desc = "The long-term objective (what you are doing)")
    context = dspy.InputField(desc = "The previous actions (what you have done)")
    purpose = dspy.InputField(desc = "The purpose of the action (what you have to do now)")
    prompt = dspy.InputField(desc = "The action specific instructions (How to do it)")
    answer = dspy.OutputField(desc = "The right answer with the right format")

class PredictTool(BaseTool):

    def __init__(self):
        super().__init__(name = "Predict")
        self.predict = dspy.Predict(PredictSignature)
    
    def forward(
            self,
            context: str,
            objective: str,
            purpose: str,
            prompt: str,
            disable_inference: bool = False,
        ) -> dspy.Prediction:
        if not disable_inference:
            pred = self.predict(
                objective = objective,
                context = context,
                purpose = purpose,
                prompt = prompt,
            )
            occurence = pred.answer.find("\n\nAnswer:")
            if occurence > 0:
                answer = pred.answer[occurence+len("\n\nAnswer:"):]
            else:
                answer = pred.answer
            answer = answer.strip()
            return dspy.Prediction(
                answer = answer
            )
        else:
            return dspy.Prediction(
                answer = prompt
            )