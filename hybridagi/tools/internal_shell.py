import dspy
from .base import BaseTool
from ..hybridstores.filesystem.filesystem import FileSystem
from ..utility.shell import ShellUtility
from ..parsers.path import PathOutputParser
from ..types.state import AgentState

class InternalShellSignature(dspy.Signature):
    """Infer the unix shell command to access your filesystem"""
    objective = dspy.InputField(desc = "The long-term objective (what you are doing)")
    context = dspy.InputField(desc = "The previous actions (what you have done)")
    purpose = dspy.InputField(desc = "The purpose of the action (what you have to do now)")
    prompt = dspy.InputField(desc = "The action specific instructions (How to do it)")
    unix_shell_command = dspy.OutputField(desc = "The name of the file to read")

class InternalShellTool(BaseTool):

    def __init__(
            self,
            filesystem: FileSystem,
            agent_state: AgentState,
        ):
        super().__init__(name = "InternalShell")
        self.predict = dspy.Predict(InternalShellSignature)
        self.agent_state = agent_state
        self.filesystem = filesystem
        self.shell = ShellUtility(
            filesystem = self.filesystem,
            agent_state = self.agent_state,
        )

    def execute(self, command: str) -> str:
        command = command.strip("`")
        s = shlex.shlex(command, punctuation_chars=True)
        args = list(s)
        invalid_symbols = ["|", "||", "&", "&&", ">", ">>", "<", "<<", ";"]
        if len(list(set(invalid_symbols).intersection(args))) > 0:
            raise ValueError(
                    "Piping, redirection and multiple commands are not supported:"+
                    " Use one command at a time, without semicolon."
                )
        try:
            return self.shell.execute(args)
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
        """Method to perform DSPy forward prediction"""
        if not disable_inference:
            prediction = self.predict(
                objective = objective,
                context = context,
                purpose = purpose,
                prompt = prompt,
            )
            observation = self.execute(prediction.unix_shell_command)
            return dspy.Prediction(
                unix_shell_command = prediction.unix_shell_command,
                observation = observation,
            )
        else:
            observation = self.execute(prompt)
            return dspy.Prediction(
                unix_shell_command = prompt,
                observation = observation,
            )

    def __deepcopy__(self, memo):
        cpy = (type)(self)(
            filesystem = self.filesystem,
            agent_state = self.agent_state,
        )
        cpy.predict = copy.deepcopy(self.predict, memo = memo)
        return cpy