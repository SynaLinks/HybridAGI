import dspy
import json
import re
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Union
from enum import Enum
from uuid import UUID, uuid4

class Query(BaseModel):
    query: str = Field(description="The input user query")

class QueryList(BaseModel, dspy.Prediction):
    queries: Optional[List[Query]] = Field(description="List of queries", default=[])

class Document(BaseModel):
    id: Union[UUID, str] = Field(description="Unique identifier for the document", default_factory=uuid4)
    text: str = Field(description="The actual text content of the document")
    parent_id: Optional[Union[UUID, str]] = Field(description="Identifier for the parent document", default=None)
    vector: Optional[List[float]] = Field(description="Vector representation of the document", default=None)
    metadata: Optional[Dict[str, Any]] = Field(description="Additional information about the document", default={})

class DocumentList(BaseModel, dspy.Prediction):
    docs: Optional[List[Document]] = Field(description="List of documents", default=[])

class QueryWithDocuments(BaseModel):
    query: Query = Field(description="The input user query")
    docs: Optional[List[Document]] = Field(description="List of documents", default=[])

class Entity(BaseModel):
    id: Union[UUID, str] = Field(description="Unique identifier for the entity", default_factory=uuid4)
    label: str = Field(description="Label or category of the entity")
    name: str = Field(description="Name or title of the entity")
    description: Optional[str] = Field(description="Description of the entity", default=None)
    vector: Optional[List[float]] = Field(description="Vector representation of the document", default=None)
    metadata: Optional[Dict[str, Any]] = Field(description="Additional information about the document", default={})

class EntityList(BaseModel, dspy.Prediction):
    entities: List[Entity] = Field(description="List of entities", default=[])
    
class QueryWithEntities(BaseModel):
    query: Query = Field(description="The input user query")
    entities: List[Entity] = Field(description="List of entities", default=[])
    
class Relationship(BaseModel):
    id: Union[UUID, str] = Field(description="Unique identifier for the relation", default_factory=uuid4)
    name: str = Field(description="Relationship name")
    inverse: str = Field(description="Opposite relation if any", default=None)
    symetric: Optional[bool] = Field(description="Either True if the relation is symetric, False otherwise or None if unknow", default=None)
    assymetric: Optional[bool] = Field(description="Either True if the relation is assymetric, False otherwise or None if unknow", default=None)
    antisymetric: Optional[bool] = Field(description="Either True if the relation is antisymetric, False otherwise or None if unknow", default=None)
    transitive: Optional[bool] = Field(description="Either True if the relation is transitive, False otherwise or None if unknow", default=None)
    vector: Optional[List[float]] = Field(description="Vector representation of the relationship", default=None)
    metadata: Optional[Dict[str, Any]] = Field(description="Additional information about the relationship", default={})

class Fact(BaseModel):
    id: Union[UUID, str] = Field(description="Unique identifier for the fact", default_factory=uuid4)
    subj: Entity = Field(description="Entity that is the subject of the fact")
    rel: Relationship = Field(description="Relation between the subject and object entities")
    obj: Entity = Field(description="Entity that is the object of the fact")
    vector: Optional[List[float]] = Field(description="Vector representation of the fact", default=None)
    metadata: Optional[Dict[str, Any]] = Field(description="Additional information about the fact", default={})

class FactList(BaseModel, dspy.Prediction):
    facts: List[Fact] = Field(description="List of facts", default=[])
    
class QueryWithFacts(BaseModel):
    query: Query = Field(description="The input user query")
    facts: List[Fact] = Field(description="List of facts", default=[])

class UserProfile(BaseModel):
    id: Union[UUID, str] = Field(description="Unique identifier for the user", default_factory=uuid4)
    name: Optional[str] = Field(description="The user name", default="Unknow")
    profile: Optional[str] = Field(description="The user profile", default="An average user")
    vector: Optional[List[float]] = Field(description="Vector representation of the user", default=None)
    metadata: Optional[Dict[str, Any]] = Field(description="Additional information about the user", default={})

class Role(str, Enum):
    AI = "AI"
    User = "User"

class Message(BaseModel):
    role: Role
    content: str

class ChatHistory(BaseModel):
    msgs: Optional[List[Message]] = Field(description="List of messages", default=[])

class InteractionSession(BaseModel):
    id: Union[UUID, str] = Field(description="Unique identifier for the interaction session", default_factory=uuid4)
    user: Optional[UserProfile] = Field(description="The user profile", default_factory=UserProfile)
    chat: Optional[ChatHistory] = Field(description="The chat history", default_factory=ChatHistory)
    
class QueryWithSession(BaseModel):
    query: Query = Field(description="The input user query")
    session: InteractionSession = Field(description="The current interaction session")

class AgentStepType(str, Enum):
    Action = "Action"
    Decision = "Decision"
    ProgramCall = "ProgramCall"
    ProgramEnd = "ProgramEnd"
    Finish = "Finish"

class AgentStep(BaseModel):
    id: Union[UUID, str] = Field(description="Unique identifier for a step", default_factory=uuid4)
    parent_id: Union[UUID, str] = Field(description="The previous step id if any", default="")
    hop: int = Field(description="The step hop")
    step_type: AgentStepType = Field(description="The step type")
    inputs: Optional[Dict[str, Any]] = Field(description="The input of the step", default=None)
    output: Optional[Dict[str, Any]] = Field(description="The output of the step", default=None)
    vector: Optional[List[float]] = Field(description="Vector representation of the step", default=None)
    metadata: Optional[Dict[str, Any]] = Field(description="Additional information about the step", default=None)

class AgentStepList(BaseModel):
    steps: List[AgentStep] = Field(description="List of agent steps", default=[])

class FinishReason(str, Enum):
    MaxIters = "max_iters"
    Finished = "finished"
    Error = "error"

class AgentOutput(BaseModel, dspy.Prediction):
    finish_reason: FinishReason = Field(description="The finish reason")
    final_answer: str = Field(description="The final answer or error if any")
    program_trace: AgentStepList = Field(description="The resulting program trace")
    session: InteractionSession = Field(description="The resulting interaction session")