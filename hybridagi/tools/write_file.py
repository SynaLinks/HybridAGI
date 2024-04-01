import dspy
from .base import BaseTool
from ..hybridstores.filesystem.filesystem import FileSystem
from ..parsers.path import PathOutputParser

class WriteFileSignature(dspy.Signature):
    """Write into a file and create it if non-existing"""
    objective = dspy.InputField(desc = "The long-term objective (what you are doing)")
    context = dspy.InputField(desc = "The previous actions (what you have done)")
    purpose = dspy.InputField(desc = "The purpose of the action (what you have to do now)")
    prompt = dspy.InputField(desc = "The action specific instructions (How to do it)")
    filename = dspy.OutputField(desc="The name of the file to write into")
    content = dspy.OutputField(desc="The content to write into the file")

class WriteFileTool(BaseTool):

    def __init__(self, filesystem: FileSystem, agent_state: AgentState):
        super().__init__(name = "WriteFile")
        self.predict = dspy.Predict(WriteFileSignature)
        self.agent_state = agent_state
        self.filesystem = filesystem
        self.path_parser = PathOutputParser()

    def write_file(self, filename: str, content: str) -> str:
        try:
            filename = self.path_parser.parse(filename)
            filename = self.agent_state.context.eval_path(filename)
            self.filesystem.add_texts(texts = [content], ids = [filename])
            return "Successfully created"
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
            observation = self.write_file(prediction.filename)
            return dspy.Prediction(
                filename = prediction.filename,
                content = prediction.content,
                observation = observation,
            )
        else:
            raise NotImplementedError("Disabling inference for WriteFile not supported")