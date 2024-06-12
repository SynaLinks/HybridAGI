"""The internal shell tool. Copyright (C) 2024 SynaLinks. License: GPL-3.0"""

import shlex
import copy
import dspy
from .base import BaseTool
from typing import Optional
from ..hybridstores.filesystem.filesystem import FileSystem
from ..utility.shell import ShellUtility
from ..output_parsers.prediction import PredictionOutputParser
from ..types.state import AgentState
from ..utility.commands import (
    ChangeDirectory,
    ListDirectory,
    MakeDirectory,
    Move,
    PrintWorkingDirectory,
    Remove,
    Tree,
)

class InternalShellSignature(dspy.Signature):
    """You will be given an objective, purpose and context
    Using the prompt to help you, you will infer the correct unix shell command, whitelist: [`cd`, `ls`, `mkdir`, `mv`, `pwd`, `rm`, `tree`]"""
    objective = dspy.InputField(desc = "The long-term objective (what you are doing)")
    context = dspy.InputField(desc = "The previous actions (what you have done)")
    purpose = dspy.InputField(desc = "The purpose of the action (what you have to do now)")
    prompt = dspy.InputField(desc = "The action specific instructions (How to do it)")
    unix_shell_command = dspy.OutputField(desc = "The unix command between [`cd`, `ls`, `mkdir`, `mv`, `pwd`, `rm`, `tree`]")

class InternalShellTool(BaseTool):

    def __init__(
            self,
            filesystem: FileSystem,
            agent_state: AgentState,
            lm: Optional[dspy.LM] = None,
        ):
        super().__init__(name = "InternalShell")
        self.predict = dspy.Predict(InternalShellSignature)
        self.agent_state = agent_state
        self.filesystem = filesystem
        self.shell = ShellUtility(
            filesystem = self.filesystem,
            agent_state = self.agent_state,
            commands = [
                ChangeDirectory(filesystem=filesystem),
                ListDirectory(filesystem=filesystem),
                MakeDirectory(filesystem=filesystem),
                Move(filesystem=filesystem),
                PrintWorkingDirectory(filesystem=filesystem),
                Remove(filesystem=filesystem),
                Tree(filesystem=filesystem),
            ]
        )
        self.prediction_parser = PredictionOutputParser()

    def execute(self, command: str) -> str:
        command = command.strip("`")
        s = shlex.shlex(command, punctuation_chars=True)
        args = list(s)
        invalid_symbols = ["|", "||", "&", "&&", ">", ">>", "<", "<<", ";"]
        invalid = False
        if len(list(set(invalid_symbols).intersection(args))) > 0:
            invalid = True
            dspy.Suggest( invalid,
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
            with dspy.context(lm=self.lm if self.lm is not None else dspy.settings.lm):
                pred = self.predict(
                    objective = objective,
                    context = context,
                    purpose = purpose,
                    prompt = prompt,
                )
            pred.unix_shell_command = self.prediction_parser.parse(
                pred.unix_shell_command,
                prefix = "Unix Shell Command:",
                stop = ["\n"],
            )
            observation = self.execute(pred.unix_shell_command)
            return dspy.Prediction(
                unix_shell_command = pred.unix_shell_command,
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
        cpy.predict = copy.deepcopy(self.predict)
        return cpy