from typing import List
from langchain.tools import BaseTool
from pydantic.v1 import BaseModel

class BaseReasoner(BaseModel):
    name: str
    description: str
    tools: List[BaseTool]