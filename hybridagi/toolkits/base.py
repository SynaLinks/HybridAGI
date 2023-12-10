from typing import List
from langchain.tools import BaseTool
from pydantic.v1 import BaseModel

class BaseToolKit(BaseModel):
    tools: List[BaseTool]