# Fact

Facts are the atomic data of a [Knowledge Graph](https://en.wikipedia.org/wiki/Knowledge_graph). They represent the relations between two entities (respectively a subject and an object). They are the basis of knowledge based systems they allow to represent precise and formal knowledge. With them you can implement Knowledge Graph based Retrieval Augmented Generation.

`Entity`: Represent an entity like a person, object, place or document to be processed or saved into memory

`Fact`: Represent a first order predicate to be processed or saved into the `FactMemory`

`EntityList`: A list of entities to be processed or saved into memory

`FactList`: A list of facts to be processed or saved into memory

## Definition
  
```python

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

class QueryWithFacts(BaseModel, dspy.Prediction):
    queries: QueryList = Field(description="The input query list", default_factory=QueryList)
    facts: Optional[List[Fact]] = Field(description="List of facts", default=[])
    
    def __init__(self, **kwargs):
        BaseModel.__init__(self, **kwargs)
        dspy.Prediction.__init__(self, **kwargs)
        
    def to_dict(self):
        return {"queries": [q.query for q in self.queries.queries], "facts": [f.to_dict() for f in self.facts]}

```

## Usage

```

```