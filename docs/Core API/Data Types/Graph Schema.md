# Graph Schema

This datatype represent a Cypher oriented Graph Schema used to constrain the generation of a LLM.

## Definition

```python
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
```