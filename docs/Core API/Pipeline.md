A pipeline is a structure that allows you to cascade DSPy modules into a sequence that you can use in other pipelines.

It have been implemented to provide a simple way of creating sequence of modules while giving you access to the modules output after processing.

### Usage:

```python
import hybridagi as hagi
from hybridagi.memory.integration.local import LocalDocumentMemory
import hybridagi.core.datatypes as dt
from hybridagi.core.pipeline import Pipeline

input_data = [
    {
        "title": "The Catcher in the Rye",
        "content": "The Catcher in the Rye is a novel by J. D. Salinger, partially published in serial form in 1945–1946 and as a novel in 1951. It is widely considered one of the greatest American novels of the 20th century. The novel's protagonist, Holden Caulfield, has become an icon for teenage rebellion and angst. The novel also deals with complex issues of innocence, identity, belonging, loss, and connection."
    },
    {
        "title": "To Kill a Mockingbird",
        "content": "To Kill a Mockingbird is a novel by Harper Lee published in 1960. It was immediately successful, winning the Pulitzer Prize, and has become a classic of modern American literature. The plot and characters are loosely based on the author's observations of her family and neighbors, as well as on an event that occurred near her hometown in 1936, when she was 10 years old. The novel is renowned for its sensitivity and depth in addressing racial injustice, class, gender roles, and destruction of innocence."
    }
]

input_docs = [dt.Document(text=d["content"], metadata={"title": d["title"]}) for d in input_data]

pipeline = Pipeline()

pipeline.add("split_chunk", hagi.DocumentSplitter(method="sentence", chunk_size=1))
pipeline.add("embed_docs", hagi.DocumentEmbedder(embeddings=embeddings))

final_docs = pipeline(input_docs)
```