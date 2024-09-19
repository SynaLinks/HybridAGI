# Session

`UserProfile`: Represent the user profile used to personalize the interaction and by the simulation of the user.
  
```python

class UserProfile(BaseModel):
	id: str = Field(description="Unique identifier for the user", default_factory=uuid4)
	name: str = Field(description="The user name", default="Unknow")
	profile: str = Field(description="The user profile", default="An average User")

class RoleType(str, Enum):
	AI = "AI"
	User = "User"

class Message(BaseModel):
	role: RoleType
	message: str

class ChatHistory(BaseModel):
	msgs: List[Message] = Field(description="List of messages", default=[])

class InteractionSession(BaseModel):
	id: str = Field(description="Unique identifier for the interaction session", default_factory=uuid4)
	user_profile: UserProfile = Field(description="The user profile")
	chat_history: ChatHistory = Field(description="The chat history")

```