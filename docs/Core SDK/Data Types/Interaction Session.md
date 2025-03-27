# Interaction Session

The interaction session represent the state of an interaction during the execution of query by the agent, it provide a way for the developers to personalize the interaction, make statefull chat application of simulate different personas to generate training data.

`UserProfile`: Represent the user profile used to personalize the interaction and to simulate different user personas.

`Role`: Represent the different roles in a conversation.

`Message`: Represent a message in a conversation.

`ChatHistory`: Represent a list of messages.

`InteractionSession`: Represent the state of an interaction session.

`QueryWithSession`: A query associated with an interaction session.

## Definition
  
```python
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
```