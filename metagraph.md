# What is the meta knowledge graph?

The meta knowledge graph, often referred to as the metagraph, is a fundamental structure that captures the current state of the AGI's hybrid memory. It serves as a hierarchical representation of documents, folders and associated structures extracted from them. Enabling the AGI to reason effectively at various levels of abstraction.

To visualize it, open your browser for RedisInsight, open RedisGraph tab and and look for the `graph:metagraph` in the graph list.

![HybridAGI's metagraph](img/metagraph.png)
The metagraph of HybridAGI containing its own codebase, in orange is the folders, in yellow the documents and in blue its content.

## RedisGraph schema
### Labels:
- Folder: Represents a folder.
- Document: Represents a document.
- Content: Represents a chunk of content.
- Graph: Represents a graph.

### Properties:
- Folder:
  - name: The name of the folder.
- Document:
  - name: The name of the document.
- Content:
  - name: The index of the content within the vector memory.
- Graph:
  - name: The index of the graph within the graph memory.

### Relationship types:
- REPRESENTS: Represents when a graph represents a content, document, or folder.
- SUMMARIZES: Represents when a content summarizes a content, document or folder
- CONTAINS: Represents the composition between contents, graphs, and folders.

- BOF: Represents the starting content of a document.
- EOF: Represents the ending content of a document
- NEXT: Represents the next content of a document