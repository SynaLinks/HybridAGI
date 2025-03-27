# Agent Step

Here is represented the datastructure used by the Agent System, usually you don't have to worry about it because it is handled automatically by the system. But for documentation purpose, here are the definition of the corresponding structure.

`AgentStep`: Represents a step performed by the Agent to be stored into memory.

`AgentStepList`: Represents a list of steps performed by the Agent.

`QueryWithSteps`: Represents a query associated with a ste list used by the action retrivers and rerankers.

## Definition
  
```python

class AgentStepType(str, Enum):
    Action = "Action"
    Decision = "Decision"
    ProgramCall = "ProgramCall"
    ProgramEnd = "ProgramEnd"
    
ACTION_TEMPLATE = \
"""--- Step {hop} ---
Action Purpose: {purpose}
Action: {prediction}"""

DECISION_TEMPLATE = \
"""--- Step {hop} ---
Decision Purpose: {purpose}
Decision: {choice}"""

CALL_PROGRAM_TEMPLATE = \
"""--- Step {hop} ---
Call Program: {program}
Program Purpose: {purpose}"""

END_PROGRAM_TEMPLATE = \
"""--- Step {hop} ---
End Program: {program}"""

class AgentStep(BaseModel):
    id: Union[UUID, str] = Field(description="Unique identifier for a step", default_factory=uuid4)
    parent_id: Optional[Union[UUID, str]] = Field(description="The previous step id if any", default=None)
    hop: int = Field(description="The step hop", default=0)
    step_type: AgentStepType = Field(description="The step type")
    inputs: Optional[Dict[str, Any]] = Field(description="The inputs of the step", default=None)
    outputs: Optional[Dict[str, Any]] = Field(description="The outputs of the step", default=None)
    vector: Optional[List[float]] = Field(description="Vector representation of the step", default=None)
    metadata: Optional[Dict[str, Any]] = Field(description="Additional information about the step", default=None)
    created_at: datetime = Field(description="Time when the step was created", default_factory=datetime.now)
    
    def __str__(self):
        if self.inputs is None:
            self.inputs = {}
        
        if self.step_type == AgentStepType.Action:
            return ACTION_TEMPLATE.format(
                hop=self.hop,
                purpose=self.inputs.get("purpose", ""),
                prediction=json.dumps(self.outputs, indent=2),
            )
        elif self.step_type == AgentStepType.Decision:
            return DECISION_TEMPLATE.format(
                hop=self.hop,
                purpose=self.inputs.get("purpose", ""),
                choice=self.outputs.get("choice", ""),
            )
        elif self.step_type == AgentStepType.ProgramCall:
            return CALL_PROGRAM_TEMPLATE.format(
                hop=self.hop,
                purpose=self.inputs.get("purpose", ""),
                program=self.inputs.get("program", ""),
            )
        elif self.step_type == AgentStepType.ProgramEnd:
            return END_PROGRAM_TEMPLATE.format(
                hop=self.hop,
                program=self.inputs.get("program", ""),
            )
        else:
            raise ValueError("Invalid type for AgentStep")
        
    def to_dict(self):
        return {"step": str(self)}

class AgentStepList(BaseModel, dspy.Prediction):
    steps: List[AgentStep] = Field(description="List of agent steps", default=[])
    
    def __init__(self, **kwargs):
        BaseModel.__init__(self, **kwargs)
        dspy.Prediction.__init__(self, **kwargs)
        
    def to_dict(self):
        return {"steps": [s.to_dict() for s in self.steps]}

class QueryWithSteps(BaseModel, dspy.Prediction):
    queries: QueryList = Field(description="The input query list", default_factory=QueryList)
    steps: List[AgentStep] = Field(description="List of agent steps", default=[])
    
    def to_dict(self):
        return {"queries": [q.query for q in self.queries.queries], "steps": [s.to_dict() for s in self.steps]}
```