import dspy

class PartiallyParametrableQuery(BaseModel):
    subj: Optional[str] = Field(description="The subject of the relation (None if unknow)", default=None)
    rel: Optional[str] = Field(description="The predicate of the relation (None if unknown)", default=None)
    obj: Optional[str] = Field(description="The object of the relation (None if unknow)", default=None)

class QueryToPartiallyParametrableQuery(dspy.Signature):
    query: str = dspy.Input(desc="The natural language query to translate into a partially parametrable query")
    fact: PartiallyParametrableQuery = dspy.Output(desc="The partially parametrable query")

class FAISSQueryFact(dspy.Module):
    
    def __init__(self):
        pass#TODO
    
    def forward(self, query: Query) -> QueryWithFacts:
        pass#TODO