# Agent Output

This data structure represent the output of the Agent (e.g. the execution of a graph program).

`FinishReason`: The different reasons for the end of a program.

`AgentOuput`: The output returned by the Agent system.

## Definition

```python
class FinishReason(str, Enum):
    MaxIters = "max_iters"
    Finished = "finished"
    Error = "error"

class AgentOutput(BaseModel, dspy.Prediction):
    finish_reason: FinishReason = Field(description="The finish reason", default=FinishReason.Finished)
    final_answer: str = Field(description="The final answer or error if any", default="")
    program_trace: AgentStepList = Field(description="The resulting program trace", default_factory=AgentStepList)
    session: InteractionSession = Field(description="The resulting interaction session", default_factory=InteractionSession)
    
    def __init__(self, **kwargs):
        BaseModel.__init__(self, **kwargs)
        dspy.Prediction.__init__(self, **kwargs)
```