# What is the meta knowledge graph?

The meta knowledge graph, often referred to as the metagraph, is a fundamental structure that captures the current state of the AGI's hybrid memory. It serves as a hierarchical representation of documents and plans, enabling the AGI to reason effectively at various levels of abstraction and follow predefined plans.

To visualize it, open you browser for RedisInsight, open RedisGraph tab and and look for the `graph:metagraph` in the graph list.

## RedisGraph schema
### Labels:
- Folder: Represents a folder.
- Document: Represents a document.
- Content: Represents a chunk of content.
- Graph: Represents a graph.
- Plan: Represents a plan.

### Properties:
- Folder:
  - name: The name of the folder.
- Document:
  - name: The name of the document.
- Content:
  - name: The index of the content within the vector memory.
- Graph:
  - name: The index of the graph within the graph memory.
- Plan:
  - name: The index of the plan within the graph memory.

### Relationship types:
- REPRESENTS: Represents when a graph represents a content, document, or folder.
- CONTAINS: Represents the composition between contents, graphs, and folders.

- BOF: Represents the starting content of a document.
- EOF: Represents the ending content of a document
- NEXT: Represents the next content of a document

- REQUIRES: Represents when a plan requires another plan.