"""The plannify tool. Copyright (C) 2024 SynaLinks. License: GPL-3.0"""

import copy
import dspy
from .base import BaseTool
from typing import Optional, Callable
from ..hybridstores.program_memory.program_memory import ProgramMemory
from ..types.state import AgentState
from ..parsers.program_name import ProgramNameOutputParser
from ..parsers.prediction import PredictionOutputParser

class PlannifySignature(dspy.Signature):
    """You will be given an objective, purpose and context.
    Using the prompt to help you, you will infer the correct plan.
    Make sure to specifiy decision making steps and their outcome."""
    objective = dspy.InputField(desc = "The long-term objective (what you are doing)")
    context = dspy.InputField(desc = "The previous actions (what you have done)")
    purpose = dspy.InputField(desc = "The purpose of the action (what you have to do now)")
    prompt = dspy.InputField(desc = "The action specific instructions (How to do it)")
    plan = dspy.OutputField(desc = "The plan to execute")

class PlannifyProgramTool(BaseTool):

    def __init__(
            self,
            program_memory: ProgramMemory,
            agent_state: AgentState,
        ):
        super().__init__(name = "Plannify")
        self.agent_state = agent_state
        self.program_memory = program_memory
        self.program_name_parser = ProgramNameOutputParser()
        self.prediction_parser = PredictionOutputParser()
        self.predict = dspy.Predict(PlannifySignature)
        self.program_tester = TesterUtility(program_memory=program_memory)

    def write_program(self, filename: str, content: str) -> str:
        try:
            self.program_tester.verify_programs(
                [filename],
                [content],
            )
            self.program_memory.add_texts(texts = [content], ids = [filename])
            return "Successfully created"
        except Exception as err:
            return str(err)

    def call_program(self, program_name: str):
        """Method to call a program"""
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
            plan = self.prediction_parser.parse(
                prediction.selected_routine, prefix="Plan:",
            )
            # TODO Convert the plan into Cypher
            raise NotImplementedError("Not implemented yet.")
        else:
            # TODO
            raise NotImplementedError("Not implemented yet.")

    def __deepcopy__(self, memo):
        cpy = (type)(self)(
            program_memory = self.program_memory,
            agent_state = self.agent_state,
        )
        cpy.predict = copy.deepcopy(self.predict)
        return cpy