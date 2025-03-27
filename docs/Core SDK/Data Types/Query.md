# Query

The Queries represent the input data for the agent system, they are also used by the retrievers and rerankers and the query engine.

`Query`: A user or LLM generated query.

`QueryList`: A list of queries.

## Definition

```python
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
```