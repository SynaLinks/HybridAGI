
`Document`: Represent an unstructured textual data to be processed or saved into the `DocumentMemory`, it can represent a text, text chunk, table row or a claim (unstructured fact)

`DocumentList`: A list of documents to be processed or saved into memory
  
```python
import dspy
from pydantic import BaseModel, Field
from typing import Optional, List, Dict

class Document(BaseModel):
	id: str = Field(description="Unique identifier for the document", default_factory=uuid4)
	text: str = Field(description="The actual text content of the document")
	parent_id: str = Field(description="Identifier for the parent document", default="")
	vector: Optional[List[float]] = Field(description="Vector representation of the document", default=None)
	metadata: Optional[Dict[str, Any]] = Field(description="Additional information about the document", default=None)

class DocumentList(BaseModel, dspy.Prediction):
	docs: List[Document] = Field(description="List of documents", default=[])

``` 

`Entity`: Represent an entity like a person, object, place or document to be processed or saved into the `FactMemory`

`Fact`: Represent a first order predicate to be processed or saved into the `FactMemory`

`FactList`: A list of facts to be processed or saved into memory
  
```python

class Entity(BaseModel):
	id: str = Field(description="Unique identifier for the entity", default_factory=uuid4)
	label: str = Field(description="Label or category of the entity")
	name: str = Field(description="Name or title of the entity")
	vector: Optional[List[float]] = Field(description="Vector representation of the entity", default=None)
	metadata: Optional[Dict[str, Any]] = Field(description="Additional information about the entity", default=None)

class Fact(BaseModel):
	id: str = Field(description="Unique identifier for the fact", default_factory=uuid4)
	subj: Entity = Field(description="Entity that is the subject of the fact")
	rel: str = Field(description="Relationship between the subject and object entities")
	obj: Entity = Field(description="Entity that is the object of the fact")
	vector: Optional[List[float]] = Field(description="Vector representation of the fact", default=None)
	metadata: Optional[Dict[str, Any]] = Field(description="Additional information about the fact", default=None)

class FactList(BaseModel, dspy.Prediction):
	facts: List[Fact] = Field(description="List of facts", default=[])

```

`UserProfile`: Represent the user profile used to personalize the interaction and 
  
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

`AgentStep`: Represent a step performed by the Agent 

`AgentInput`: The DSPy input type for agents

`AgentOutput`: The DSPy output type for agents
  
```python

class AgentStepType(str, Enum):
	Action = "Action"
	Decision = "Decision"
	ProgramCall = "ProgramCall"
	ProgramEnd = "ProgramEnd"
	Finish = "Finish"

class AgentStep(BaseModel):
	id: str = Field(description="Unique identifier for a step", default_factory=uuid4)
	parent_id: str = Field(description="The previous step id if any", default="")
	hop: int = Field(description="The step hop", default=0)
	step_type: AgentStepType = Field(description="The step type")
	inputs: dspy.Prediction = Field(description="The input of the step", default=None)
	output: dspy.Prediction = Field(description="The output of the step", default=None)
	vector: Optional[List[float]] = Field(description="Vector representation of the step", default=None)
	metadata: Optional[Dict[str, Any]] = Field(description="Additional information about the step", default=None)

class ProgramTrace(BaseModel):
	steps: List[AgentStep] = Field(description="List of agent steps", default=[])

class FinishReason(str, Enum):
	MaxIters = "max_iters"
	Finished = "finished"
	Error = "error"

class UserQuery(BaseModel):
	query: str = Field(description="The User query")

class AgentInput():
	objective: UserQuery = Field(description="The user objective")
	session: InteractionSession = Field(description="The current interaction session", default=None)

class AgentOutput(BaseModel, dspy.Prediction):
	finish_reason: FinishReason = Field(description="The finish reason")
	final_answer: str = Field(description="The final answer or error if any")
	program_trace: ProgramTrace = Field(description="The resulting program trace")
	session: InteractionSession = Field(description="The resulting interaction session")

```
