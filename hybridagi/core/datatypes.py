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

CYPHER_FACT_REGEX = r'\(:(\w+)\s*{name:"(.*?)"}\)\s*-\[:(\w+)\]->\s*\(:(\w+)\s*{name:"(.*?)"}\)'
CYPHER_SCHEMA_REGEX = r'\(:(\w+)\)\s*-\[:(\w+)\]->\s*\(:(\w+)\)'

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
        
    def to_dict(self):
        return {"queries": [q.query for q in self.queries]}

class Document(BaseModel):
    id: Union[UUID, str] = Field(description="Unique identifier for the document", default_factory=uuid4)
    text: str = Field(description="The actual text content of the document")
    parent_id: Optional[Union[UUID, str]] = Field(description="Identifier for the parent document", default=None)
    vector: Optional[List[float]] = Field(description="Vector representation of the document", default=None)
    metadata: Optional[Dict[str, Any]] = Field(description="Additional information about the document", default={})
    
    def to_dict(self):
        if self.metadata:
            return {"text": self.text, "metadata": self.metadata}
        else:
            return {"text": self.text}

class DocumentList(BaseModel, dspy.Prediction):
    docs: Optional[List[Document]] = Field(description="List of documents", default=[])
    
    def __init__(self, **kwargs):
        BaseModel.__init__(self, **kwargs)
        dspy.Prediction.__init__(self, **kwargs)
        
    def to_dict(self):
        return {"documents": [d.to_dict() for d in self.docs]}

class QueryWithDocuments(BaseModel, dspy.Prediction):
    queries: QueryList = Field(description="The input query list", default_factory=QueryList)
    docs: Optional[List[Document]] = Field(description="List of documents", default=[])
    
    def __init__(self, **kwargs):
        BaseModel.__init__(self, **kwargs)
        dspy.Prediction.__init__(self, **kwargs)
        
    def to_dict(self):
        return {"queries": [q.query for q in self.queries.queries], "documents": [d.to_dict() for d in self.docs]}

class Entity(BaseModel):
    id: Union[UUID, str] = Field(description="Unique identifier for the entity", default_factory=uuid4)
    label: str = Field(description="Label or category of the entity")
    name: str = Field(description="Name or title of the entity")
    description: Optional[str] = Field(description="Description of the entity", default=None)
    vector: Optional[List[float]] = Field(description="Vector representation of the document", default=None)
    metadata: Optional[Dict[str, Any]] = Field(description="Additional information about the document", default={})
    
    def to_dict(self):
        if self.metadata:
            if self.description is not None:
                return {"name": self.name, "label": self.label, "description": self.description, "metadata": self.metadata}
            else:
                return {"name": self.name, "label": self.label, "metadata": self.metadata}
        else:
            if self.description is not None:
                return {"name": self.name, "label": self.label, "description": self.description}
            else:
                return {"name": self.name, "label": self.label}

class EntityList(BaseModel, dspy.Prediction):
    entities: List[Entity] = Field(description="List of entities", default=[])
    
    def __init__(self, **kwargs):
        BaseModel.__init__(self, **kwargs)
        dspy.Prediction.__init__(self, **kwargs)
        
    def to_dict(self):
        return {"entities": [e.to_dict() for e in self.entities]}
    
class QueryWithEntities(BaseModel, dspy.Prediction):
    queries: QueryList = Field(description="The input query list", default_factory=QueryList)
    entities: List[Entity] = Field(description="List of entities", default=[])
    
    def __init__(self, **kwargs):
        BaseModel.__init__(self, **kwargs)
        dspy.Prediction.__init__(self, **kwargs)
    
    def to_dict(self):
        return {"queries": [q.query for q in self.queries.queries], "entities": [e.to_dict() for e in self.entities]}
    
class Relationship(BaseModel):
    id: Union[UUID, str] = Field(description="Unique identifier for the relation", default_factory=uuid4)
    name: str = Field(description="Relationship name")
    vector: Optional[List[float]] = Field(description="Vector representation of the relationship", default=None)
    metadata: Optional[Dict[str, Any]] = Field(description="Additional information about the relationship", default={})
    
    def to_dict(self):
        if self.metadata:
            return {"name": self.name, "metadata": self.metadata}
        else:
            return {"name": self.name}

class Fact(BaseModel):
    id: Union[UUID, str] = Field(description="Unique identifier for the fact", default_factory=uuid4)
    subj: Entity = Field(description="Entity that is the subject of the fact", default=None)
    rel: Relationship = Field(description="Relation between the subject and object entities", default=None)
    obj: Entity = Field(description="Entity that is the object of the fact", default=None)
    vector: Optional[List[float]] = Field(description="Vector representation of the fact", default=None)
    metadata: Optional[Dict[str, Any]] = Field(description="Additional information about the fact", default={})
    
    def to_cypher(self) -> str:
        if self.subj.description is not None:
            subj = "(:"+self.subj.label+" {name:\""+self.subj.name+"\", description:\""+self.subj.description+"\"})"
        else:
            subj = "(:"+self.subj.label+" {name:\""+self.subj.name+"\"})"
        if self.obj.description is not None:
            obj = "(:"+self.obj.label+" {name:\""+self.obj.name+"\", description:\""+self.obj.description+"\"})"
        else:
            obj = "(:"+self.obj.label+" {name:\""+self.obj.name+"\"})"
        return subj+"-[:"+self.rel.name+"]->"+obj
    
    def from_cypher(self, cypher_fact:str, metadata: Dict[str, Any] = {}) -> "Fact":
        match = re.match(CYPHER_FACT_REGEX, cypher_fact)
        if match:
            self.subj = Entity(label=match.group(1), name=match.group(2))
            self.rel = Relationship(name=match.group(3))
            self.obj = Entity(label=match.group(4), name=match.group(5))
            self.metadata = metadata
            return self
        else:
            raise ValueError("Invalid Cypher fact provided")
    
    def to_dict(self):
        if self.metadata:
            return {"fact": self.to_cypher(), "metadata": self.metadata}
        else:
            return {"fact": self.to_cypher()}

class FactList(BaseModel, dspy.Prediction):
    facts: List[Fact] = Field(description="List of facts", default=[])
    
    def __init__(self, **kwargs):
        BaseModel.__init__(self, **kwargs)
        dspy.Prediction.__init__(self, **kwargs)
        
    def to_cypher(self) -> str:
        return ",\n".join([f.to_cypher() for f in self.facts])
    
    def from_cypher(self, cypher_facts: str, metadata: Dict[str, Any] = {}):
        triplets = re.findall(CYPHER_FACT_REGEX, cypher_facts)
        for triplet in triplets:
            subject_label, subject_name, predicate, object_label, object_name = triplet
            self.facts.append(Fact(
                subj = Entity(name=subject_name, label=subject_label),
                rel = Relationship(name=predicate),
                obj = Entity(name=object_name, label=object_label),
                metadata = metadata,
            ))
        return self
    
    def to_dict(self):
        return {"facts": [f.to_dict() for f in self.facts]}
    
class FactSchema(BaseModel):
    source: str
    predicate: str
    target: str
    
    def to_cypher(self) -> str:
        return "(:"+self.source+")-[:"+self.predicate+"]->(:"+self.target+")"
    
    def from_cypher(self, cypher_schema: str) -> "FactSchema":
        match = re.match(CYPHER_SCHEMA_REGEX, cypher_schema)
        if match:
            self.source = match.group(1)
            self.predicate = match.group(2)
            self.target = match.group(3)
            return self
        else:
            ValueError("Invalid Cypher schema provided")
        
    def is_valid(self, fact: Fact):
        if fact.subj.label != self.source:
            return False
        if fact.rel.name != self.rel:
            return False
        if fact.obj.label != self.target:
            return False
        return True
    
    def to_dict(self):
        return {"fact_schema": self.to_cypher()}
   
class GraphSchema(BaseModel, dspy.Prediction):
    schemas: Optional[List[FactSchema]] = Field(description="The graph schema", default=[])
    
    def __init__(self, **kwargs):
        BaseModel.__init__(self, **kwargs)
        dspy.Prediction.__init__(self, **kwargs)
        
    def to_cypher(self) -> str:
        return ",\n".join([s.to_cypher() for s in self.schemas])
    
    def from_cypher(self, cypher_schema: str) -> "GraphSchema":
        graph_schema = re.findall(CYPHER_SCHEMA_REGEX, cypher_schema)
        self.schemas = []
        for schema in graph_schema:
            subject_label, predicate, object_label = schema
            self.schemas.append(FactSchema(
                subj = subject_label,
                predicate = predicate,
                obj = object_label,
            ))
        return self
    
    def to_dict(self):
        return {"schema": [s.to_dict() for s in self.schemas]}
    
class QueryWithFacts(BaseModel, dspy.Prediction):
    queries: QueryList = Field(description="The input query list", default_factory=QueryList)
    facts: Optional[List[Fact]] = Field(description="List of facts", default=[])
    
    def __init__(self, **kwargs):
        BaseModel.__init__(self, **kwargs)
        dspy.Prediction.__init__(self, **kwargs)
        
    def to_dict(self):
        return {"queries": [q.query for q in self.queries.queries], "facts": [f.to_dict() for f in self.facts]}

class UserProfile(BaseModel):
    id: Union[UUID, str] = Field(description="Unique identifier for the user", default_factory=uuid4)
    name: Optional[str] = Field(description="The user name", default="Unknow")
    profile: Optional[str] = Field(description="The user profile", default="An average user")
    vector: Optional[List[float]] = Field(description="Vector representation of the user", default=None)
    metadata: Optional[Dict[str, Any]] = Field(description="Additional information about the user", default={})
    
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
    
    def to_dict(self):
        return {"user": self.user.to_dict(), "chat_history": [m.to_dict() for m in self.chat.msgs]}
    
class QueryWithSession(BaseModel, dspy.Prediction):
    query: Query = Field(description="The input user query", default_factory=Query)
    session: InteractionSession = Field(description="The current interaction session", default_factory=InteractionSession)
    
    def __init__(self, **kwargs):
        BaseModel.__init__(self, **kwargs)
        dspy.Prediction.__init__(self, **kwargs)
        
    def to_dict(self):
        return {"query": self.query.query, "session": self.session.to_dict()}

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
        
class GraphProgramList(BaseModel, dspy.Prediction):
    progs: Optional[List[GraphProgram]] = Field(description="List of graph programs", default=[])
    
    def to_dict(self):
        return {"routines": [p.to_dict() for p in self.progs]}
    
class QueryWithGraphPrograms(BaseModel, dspy.Prediction):
    queries: QueryList = Field(description="The input query list", default_factory=QueryList)
    progs: Optional[List[GraphProgram]] = Field(description="List of graph programs", default=[])
    
    def __init__(self, **kwargs):
        BaseModel.__init__(self, **kwargs)
        dspy.Prediction.__init__(self, **kwargs)
        
    def to_dict(self):
        return {"queries": [q.query for q in self.queries.queries], "routines": [p.to_dict() for p in self.progs]}
