import dspy
import json
import re
from datetime import datetime
from collections import deque
from pydantic import BaseModel, Field
from typing import Optional, Iterable, List, Dict, Any, Union
from enum import Enum
from uuid import UUID, uuid4
from hybridagi.core.graph_program import (
    GraphProgram,
    Control,
    Action,
    Decision,
    Program,
)

class Query(BaseModel, dspy.Prediction):
    query: str = Field(description="The input query", default="")
    
    def __init__(self, **kwargs):
        BaseModel.__init__(self, **kwargs)
        dspy.Prediction.__init__(self, **kwargs)

class QueryList(BaseModel, dspy.Prediction):
    queries: Optional[List[Query]] = Field(description="List of queries", default=[])
    
    def __init__(self, **kwargs):
        BaseModel.__init__(self, **kwargs)
        dspy.Prediction.__init__(self, **kwargs)

class Document(BaseModel):
    id: Union[UUID, str] = Field(description="Unique identifier for the document", default_factory=uuid4)
    text: str = Field(description="The actual text content of the document")
    parent_id: Optional[Union[UUID, str]] = Field(description="Identifier for the parent document", default=None)
    vector: Optional[List[float]] = Field(description="Vector representation of the document", default=None)
    metadata: Optional[Dict[str, Any]] = Field(description="Additional information about the document", default={})
    created_at: datetime = Field(description="Time when the document was created", default_factory=datetime.now)
    
    def to_dict(self):
        return {"text": self.text, "metadata": self.metadata}

class DocumentList(BaseModel, dspy.Prediction):
    docs: Optional[List[Document]] = Field(description="List of documents", default=[])
    
    def __init__(self, **kwargs):
        BaseModel.__init__(self, **kwargs)
        dspy.Prediction.__init__(self, **kwargs)
        
    def to_dict(self):
        return {"documents": [d.to_dict() for d in self.docs]}

class QueryWithDocuments(BaseModel, dspy.Prediction):
    query: Query = Field(description="The input query", default_factory=Query)
    docs: Optional[List[Document]] = Field(description="List of documents", default=[])
    
    def __init__(self, **kwargs):
        BaseModel.__init__(self, **kwargs)
        dspy.Prediction.__init__(self, **kwargs)
        
    def to_dict(self):
        return {"query": self.query.query, "documents": [d.to_dict() for d in self.docs]}

class Entity(BaseModel):
    id: Union[UUID, str] = Field(description="Unique identifier for the entity", default_factory=uuid4)
    label: str = Field(description="Label or category of the entity")
    name: str = Field(description="Name or title of the entity")
    description: Optional[str] = Field(description="Description of the entity", default=None)
    vector: Optional[List[float]] = Field(description="Vector representation of the document", default=None)
    metadata: Optional[Dict[str, Any]] = Field(description="Additional information about the document", default={})
    created_at: datetime = Field(description="Time when the entity was created", default_factory=datetime.now)
    
    def to_dict(self):
        if self.description is not None:
            return {"name": self.name, "label": self.label, "description": self.description, "metadata": self.metadata}
        else:
            return {"name": self.name, "label": self.label, "metadata": self.metadata}

class EntityList(BaseModel, dspy.Prediction):
    entities: List[Entity] = Field(description="List of entities", default=[])
    
    def __init__(self, **kwargs):
        BaseModel.__init__(self, **kwargs)
        dspy.Prediction.__init__(self, **kwargs)
        
    def to_dict(self):
        return {"entities": [e.to_dict() for e in self.entities]}
    
class QueryWithEntities(BaseModel, dspy.Prediction):
    query: Query = Field(description="The input query", default_factory=Query)
    entities: List[Entity] = Field(description="List of entities", default=[])
    
    def __init__(self, **kwargs):
        BaseModel.__init__(self, **kwargs)
        dspy.Prediction.__init__(self, **kwargs)
    
    def to_dict(self):
        return {"query": self.query.query, "entities": [e.to_dict() for e in self.entities]}
    
class Relationship(BaseModel):
    id: Union[UUID, str] = Field(description="Unique identifier for the relation", default_factory=uuid4)
    name: str = Field(description="Relationship name")
    vector: Optional[List[float]] = Field(description="Vector representation of the relationship", default=None)
    metadata: Optional[Dict[str, Any]] = Field(description="Additional information about the relationship", default={})
    created_at: datetime = Field(description="Time when the relationship was created", default_factory=datetime.now)
    
    def to_dict(self):
        return {"name": self.name, "metadata": self.metadata}

class Fact(BaseModel):
    id: Union[UUID, str] = Field(description="Unique identifier for the fact", default_factory=uuid4)
    subj: Entity = Field(description="Entity that is the subject of the fact")
    rel: Relationship = Field(description="Relation between the subject and object entities")
    obj: Entity = Field(description="Entity that is the object of the fact")
    weight: float = Field(description="The fact weight (between 0.0 and 1.0, default 1.0)", default=1.0)
    vector: Optional[List[float]] = Field(description="Vector representation of the fact", default=None)
    metadata: Optional[Dict[str, Any]] = Field(description="Additional information about the fact", default={})
    created_at: datetime = Field(description="Time when the fact was created", default_factory=datetime.now)
    
    def to_dict(self):
        return {"fact": "(:"+self.subj.label+" {name:\""+self.subj.name+"\"})-[:"+self.rel.name+"]->(:"+self.obj.label+" {name:\""+self.obj.name+"\"})"}

class FactList(BaseModel, dspy.Prediction):
    facts: List[Fact] = Field(description="List of facts", default=[])
    
    def __init__(self, **kwargs):
        BaseModel.__init__(self, **kwargs)
        dspy.Prediction.__init__(self, **kwargs)
        
    def to_dict(self):
        return {"facts": [f.to_dict() for f in self.facts]}
    
class QueryWithFacts(BaseModel, dspy.Prediction):
    query: Query = Field(description="The input query", default_factory=Query)
    facts: Optional[List[Fact]] = Field(description="List of facts", default=[])
    
    def __init__(self, **kwargs):
        BaseModel.__init__(self, **kwargs)
        dspy.Prediction.__init__(self, **kwargs)
        
    def to_dict(self):
        return {"query": self.query.query, "facts": [f.to_dict() for f in self.facts]}

class UserProfile(BaseModel):
    id: Union[UUID, str] = Field(description="Unique identifier for the user", default_factory=uuid4)
    name: Optional[str] = Field(description="The user name", default="Unknow")
    profile: Optional[str] = Field(description="The user profile", default="An average user")
    vector: Optional[List[float]] = Field(description="Vector representation of the user", default=None)
    metadata: Optional[Dict[str, Any]] = Field(description="Additional information about the user", default={})
    created_at: datetime = Field(description="Time when the user profile was created", default_factory=datetime.now)
    
    def to_dict(self):
        return {"name": self.name, "profile": self.profile, "metadata": self.metadata}

class Role(str, Enum):
    AI = "AI"
    User = "User"

class Message(BaseModel):
    role: Role = Field(description="The role (AI or User)")
    content: str = Field(description="The message content")
    created_at: datetime = Field(description="Time when the message was created", default_factory=datetime.now)
    
    def to_dict(self):
        return {"message": "["+self.role+"]: "+self.content}

class ChatHistory(BaseModel):
    msgs: Optional[List[Message]] = Field(description="List of messages", default=[])
    
    def to_dict(self):
        return {"messages": [m.to_dict() for m in self.msgs]}

class InteractionSession(BaseModel):
    id: Union[UUID, str] = Field(description="Unique identifier for the interaction session", default_factory=uuid4)
    user: Optional[UserProfile] = Field(description="The user profile", default_factory=UserProfile)
    chat: Optional[ChatHistory] = Field(description="The chat history", default_factory=ChatHistory)
    
    def to_dict():
        return {"user": self.user.to_dict(), "chat_history": [m.to_dict() for m in self.msgs]}
    
class QueryWithSession(BaseModel, dspy.Prediction):
    query: Query = Field(description="The input user query", default_factory=Query)
    session: InteractionSession = Field(description="The current interaction session", default_factory=InteractionSession)
    
    def __init__(self, **kwargs):
        BaseModel.__init__(self, **kwargs)
        dspy.Prediction.__init__(self, **kwargs)
        
    def to_dict(self):
        return {"query": self.query.query, "session": session.to_dict()}

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
Decision Question: {question}
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
    parent_id: Union[UUID, str] = Field(description="The previous step id if any", default=None)
    hop: int = Field(description="The step hop", default=0)
    step_type: AgentStepType = Field(description="The step type")
    weight: float = Field(description="The step weight (between 0.0 and 1.0, default 1.0)", default=1.0)
    inputs: Optional[Dict[str, Any]] = Field(description="The inputs of the step", default=None)
    outputs: Optional[Dict[str, Any]] = Field(description="The outputs of the step", default=None)
    vector: Optional[List[float]] = Field(description="Vector representation of the step", default=None)
    metadata: Optional[Dict[str, Any]] = Field(description="Additional information about the step", default=None)
    created_at: datetime = Field(description="Time when the step was created", default_factory=datetime.now)
    
    def __str__(self):
        if self.step_type == AgentStepType.Action:
            return ACTION_TEMPLATE.format(
                hop=self.hop,
                purpose=self.inputs["purpose"],
                prediction=json.dumps(self.outputs, indent=2),
            )
        elif self.step_type == AgentStepType.Decision:
            return DECISION_TEMPLATE.format(
                hop=self.hop,
                purpose=self.inputs["purpose"],
                question=self.inputs["question"],
                choice=self.outputs["choice"],
            )
        elif self.step_type == AgentStepType.ProgramCall:
            return CALL_PROGRAM_TEMPLATE.format(
                hop=self.hop,
                purpose=self.inputs["purpose"],
                program=self.inputs["program"],
            )
        elif self.step_type == AgentStepType.ProgramEnd:
            return END_PROGRAM_TEMPLATE.format(
                hop=self.hop,
                program=self.inputs["program"],
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
    query: Query = Field(description="The input query", default_factory=Query)
    steps: List[AgentStep] = Field(description="List of agent steps", default=[])
    
    def to_dict(self):
        return {"query": self.query.query, "steps": [s.to_dict() for s in self.steps]}
    
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
    
class ToolInput(BaseModel):
    objective: str = Field(description="The long-term objective (What you are doing)")
    purpose: str = Field(description="The short-term objective (What you have to do now)")
    context: str = Field(description="The last actions (What you have done)")
    prompt: str = Field(description="The additional instructions (How to do it)")
    disable_inference: bool = Field(description="Weither or not to disable inference (default False)", default=False)

class ProgramState(BaseModel):
    current_program: GraphProgram
    current_step: Union[Control, Action, Decision, Program]

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
        
class GraphProgramList(BaseModel, dspy.Prediction):
    progs: Optional[List[GraphProgram]] = Field(description="List of graph programs", default=[])
    
    def to_dict(self):
        return {"routines": [p.to_dict() for p in self.progs]}
    
class QueryWithGraphPrograms(BaseModel, dspy.Prediction):
    query: Query = Field(description="The input query", default_factory=Query)
    progs: Optional[List[GraphProgram]] = Field(description="List of graph programs", default=[])
    
    def __init__(self, **kwargs):
        BaseModel.__init__(self, **kwargs)
        dspy.Prediction.__init__(self, **kwargs)
        
    def to_dict(self):
        return {"query": self.query.query, "routines": [p.to_dict() for p in self.progs]}