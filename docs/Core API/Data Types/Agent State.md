# Agent State

This data structure represent the state of the Agent, which contains a stack allowing the agent to jump to other programs by calling them.

`ProgramState`: Represents the state of an executed program.

`AgentState`: Represents the state of the agent.

## Definition

```python

class ProgramState(BaseModel):
    current_program: GraphProgram = Field(description="The current program")
    current_step: Union[Control, Action, Decision, Program] = Field(description="The current step")

class AgentState(BaseModel):
    current_hop: int = Field(description="The current hop", default=0)
    decision_hop: int = Field(description="The current decision hop", default=0)
    program_trace: AgentStepList = Field(description="The program trace", default_factory=AgentStepList)
    program_stack: Iterable[ProgramState] = Field(description="The program stack", default=deque())
    objective: Query = Field(description="The user objective query", default_factory=Query)
    final_answer: str = Field(description="The agent final answer", default="")
    variables: Dict[str, Any] = Field(description="The variables of the program", default={})
    session: InteractionSession = Field(description="The current interaction session", default_factory=InteractionSession)
    
    def get_current_state(self) -> Optional[ProgramState]:
        """Method to get the current program state"""
        if len(self.program_stack) > 0:
            return self.program_stack[-1]
        return None
    
    def get_current_program(self) -> Optional[GraphProgram]:
        """Method to retreive the current program from the stack"""
        if len(self.program_stack) > 0:
            return self.program_stack[-1].current_program
        return None
    
    def get_current_step(self) -> Optional[Union[Control, Action, Decision, Program]]:
        """Method to retreive the current node from the stack"""
        if len(self.program_stack) > 0:
            return self.program_stack[-1].current_step
        return None
    
    def set_current_step(self, step: Union[Control, Action, Decision, Program]):
        """Method to set the current node from the stack"""
        if len(self.program_stack) > 0:
            self.program_stack[-1].current_step = step
        else:
            raise ValueError("Cannot set the current step when program finished")
    
    def call_program(self, program: GraphProgram):
        """Method to call a program"""
        self.program_stack.append(
            ProgramState(
                current_program = program,
                current_step = program.get_starting_step(),
            )
        )
        
    def end_program(self):
        """Method to end the current program (pop the stack)"""
        self.program_stack.pop()
```