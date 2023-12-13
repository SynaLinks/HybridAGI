"""The trace memory toolkit. Copyright (C) 2023 SynaLinks. License: GPL-3.0"""

from .base import BaseToolKit
from langchain.tools import Tool
from ..hybridstores.trace_memory.trace_memory import TraceMemory

class TraceMemoryToolKit(BaseToolKit):
    trace_memory: TraceMemory

    def __init__(self, trace_memory: TraceMemory):
        update_objective_tool = Tool(
            name = "UpdateObjective",
            description = \
                "Usefull to update your long-term objective. "+\
                "The Input should be the new objective",
            func=self.update_objective_tool)
        update_note_tool = Tool(
            name = "UpdateNote",
            description = \
                "Usefull to update your notes. "+\
                "The Input should be the new note",
            func=self.update_note_tool)
        clear_trace_tool = Tool(
            name = "ClearTrace",
            description = \
                "Usefull to clean up your working memory when making many errors. "+\
                "No Input needed (should be N/A)",
            func=self.clear_trace_tool)
        revert_trace_tool = Tool(
            name = "RevertTrace",
            description = \
                "Usefull to revert your last reasoning steps. "+\
                "The Input should be an integer representing the number of steps to revert",
            func=self.revert_trace_tool)
        
        tools = [
            update_objective_tool,
            update_note_tool,
            clear_trace_tool,
            revert_trace_tool,
        ]

        super().__init__(
            trace_memory = trace_memory,
            tools = tools
        )

    def update_objective_tool(self, objective: str):
        self.trace_memory.update_objective(objective)
        return "Objective successfully updated"

    def update_note_tool(self, note: str):
        self.trace_memory.update_note(note)
        return "Note successfully updated"

    def revert_trace_tool(self, n_steps: str):
        n = int(n_steps)
        self.trace_memory.revert(n)
        return f"Successfully reverted {n} steps"

    def clear_trace_tool(self, _):
        self.trace_memory.clear()
        return "Working memory cleaned sucessfully"