# Document

Documents are the atomic data used in HybridAGI's Document Memory, they are used to represent textual data and their chunks in the system. Allowing the system to implement vector-only [Retrieval Augmented Generation](https://en.wikipedia.org/wiki/Retrieval-augmented_generation) systems.

`Document`: Represent an unstructured textual data to be processed or saved into memory

`DocumentList`: A list of documents to be processed or saved into memory
  
## Definition

```python

class Document(BaseModel):
    id: Union[UUID, str] = Field(description="Unique identifier for the document", default_factory=uuid4)
    text: str = Field(description="The actual text content of the document")
    parent_id: Optional[Union[UUID, str]] = Field(description="Identifier for the parent document", default=None)
    vector: Optional[List[float]] = Field(description="Vector representation of the document", default=None)
    metadata: Optional[Dict[str, Any]] = Field(description="Additional information about the document", default={})
    
    def to_dict(self):
        if self.metadata:
            return {"text": self.text, "metadata": self.metadata}
        else:
            return {"text": self.text}

class DocumentList(BaseModel, dspy.Prediction):
    docs: Optional[List[Document]] = Field(description="List of documents", default=[])
    
    def __init__(self, **kwargs):
        BaseModel.__init__(self, **kwargs)
        dspy.Prediction.__init__(self, **kwargs)
        
    def to_dict(self):
        return {"documents": [d.to_dict() for d in self.docs]}

```

## Usage

```python

input_data = \
[
    {
        "title": "The Catcher in the Rye",
        "content": "The Catcher in the Rye is a novel by J. D. Salinger, partially published in serial form in 1945–1946 and as a novel in 1951. It is widely considered one of the greatest American novels of the 20th century. The novel's protagonist, Holden Caulfield, has become an icon for teenage rebellion and angst. The novel also deals with complex issues of innocence, identity, belonging, loss, and connection."
    },
    {
        "title": "To Kill a Mockingbird",
        "content": "To Kill a Mockingbird is a novel by Harper Lee published in 1960. It was immediately successful, winning the Pulitzer Prize, and has become a classic of modern American literature. The plot and characters are loosely based on the author's observations of her family and neighbors, as well as on an event that occurred near her hometown in 1936, when she was 10 years old. The novel is renowned for its sensitivity and depth in addressing racial injustice, class, gender roles, and destruction of innocence."
    }
]

document_list = DocumentList()

for data in input_data:
    document_list.docs.append(
        Document(
            text=data["content"],
            metadata={"title": data["title"]},
        )
    )

>>>
```