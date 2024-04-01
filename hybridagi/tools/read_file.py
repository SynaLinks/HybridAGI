import dspy
from .base import BaseTool
from ..hybridstores.filesystem.filesystem import FileSystem
from ..utility.reader import ReaderUtility
from ..parsers.path import PathOutputParser

class ReadFileSignature(dspy.Signature):
    """Infer the name of the file to read"""
    objective = dspy.InputField(desc = "The long-term objective (what you are doing)")
    context = dspy.InputField(desc = "The previous actions (what you have done)")
    purpose = dspy.InputField(desc = "The purpose of the action (what you have to do now)")
    prompt = dspy.InputField(desc = "The action specific instructions (How to do it)")
    filename = dspy.OutputField(desc="The name of the file to read")

class ReadFileTool(BaseTool):

    def __init__(self, filesystem: FileSystem, agent_state: AgentState):
        super().__init__(name = "ReadFile")
        self.predict = dspy.Predict(ReadFileSignature)
        self.agent_state = agent_state
        self.filesystem = filesystem
        self.reader = ReaderUtility(filesystem=self.filesystem)
        self.path_parser = PathOutputParser()

    def read_file(self, path: str) -> str:
        try:
            path = self.path_parser.parse(path)
            path = self.agent_state.context.eval_path(path)
            return self.reader.read_document(path)
        except Exception as err:
            return str(err)
    
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
            observation = self.read_file(prediction.filename)
            return dspy.Prediction(
                answer = prediction.filename,
                observation = observation,
            )
        else:
            observation = self.read_file(prompt)
            return dspy.Prediction(
                answer = prompt,
                observation = observation,
            )