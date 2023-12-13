"""The program memory toolkit. Copyright (C) 2023 SynaLinks. License: GPL-3.0"""

from .base import BaseToolKit
from ..hybridstores.program_memory.program_memory import ProgramMemory
from ..tools.load_programs import LoadProgramsTool
from ..tools.program_search import ProgramSearchTool
from ..tools.read_program import ReadProgramTool

class ProgramMemoryToolKit(BaseToolKit):
    program_memory: ProgramMemory

    def __init__(self, program_memory: ProgramMemory):

        load_programs_tool = LoadProgramsTool(
            program_memory = program_memory)

        program_search_tool = ProgramSearchTool(
            program_memory = program_memory)

        read_program_tool = ReadProgramTool(
            program_memory = program_memory)

        tools = [
            load_programs_tool,
            program_search_tool,
            read_program_tool,
        ]

        super().__init__(
            program_memory = program_memory,
            tools = tools,
        )