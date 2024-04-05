"""The call program tool. Copyright (C) 2024 SynaLinks. License: GPL-3.0"""

import dspy
from .base import BaseTool
from typing import Optional, Callable
from hybridagi import ProgramMemory
from ..types.state import AgentState
from ..parsers.program_name import ProgramNameOutputParser

class CallProgramSignature(dspy.Signature):
    """Select the program to execute"""
    objective = dspy.InputField(desc = "The long-term objective (what you are doing)")
    context = dspy.InputField(desc = "The previous actions (what you have done)")
    purpose = dspy.InputField(desc = "The purpose of the action (what you have to do now)")
    prompt = dspy.InputField(desc = "The action specific instructions (How to do it)")
    selected_program = dspy.OutputField(desc = "The selected program")

class CallProgramTool(BaseTool):

    def __init__(
            self,
            program_memory: ProgramMemory,
            agent_state: AgentState,
        ):
        super().__init__(name = "CallProgram")
        self.agent_state = agent_state
        self.program_memory = program_memory
        self.program_name_parser = ProgramNameOutputParser()
        self.predict = dspy.Predict(CallProgramSignature)

    def call_program(self, program_name: str):
        """Method to call a program"""
        program_name = self.program_name_parser.parse(program_name)
        if not self.program_memory.exists(program_name):
            return "Error occured: This program does not exist, verify its name"
        if self.program_memory.is_protected(program_name):
            return "Error occured: Trying to call a protected program"
        current_program = self.agent_state.get_current_program()
        current_node = self.agent_state.get_current_node()
        next_node = self.program_memory.get_next_node(current_node, current_program)
        self.agent_state.set_current_node(next_node)
        called_program = self.program_memory.get_graph(program_name)
        first_node = self.program_memory.get_starting_node(program_name)
        self.agent_state.call_program(first_node, called_program)
        return "Successfully called"
        
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
                context = context,
                objective = objective,
                purpose = purpose,
                prompt = prompt,
            )
            observation = self.call_program(prediction.selected_program)
            return dspy.Prediction(
                selected_program = prediction.selected_program,
                observation = observation,
            )
        else:
            observation = self.call_program(prompt)
            return dspy.Prediction(
                selected_program = prompt,
                observation = observation,
            )