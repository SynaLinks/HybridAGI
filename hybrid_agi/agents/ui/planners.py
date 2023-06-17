import chainlit as cl
from hybrid_agi.agents.planners.htn_planner import HTNPlanner

class UIHTNPlanner(HTNPlanner):

    def execute_task(self, task_name: str, task_purpose: str):
        task_result = super().execute_task(task_name, task_purpose)
        cl.Message(content = f"Intermediary result: {task_result}").send()
        return task_result

    def run(self, objective: str):
        final_result = super().run(objective)
        cl.Message(content = f"Final result: {final_result}").send()
        return final_result