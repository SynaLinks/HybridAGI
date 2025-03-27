# Local Memory

The local memory uses [NetworkX](https://networkx.org/), its aim is to provide an easy way to prototype your agent before using a proper graph database into production.

## Usage

```python
from hybridagi.memory.integration.local import (
    LocalProgramMemory,
    LocalDocumentMemory,
    LocalFactMemory,
    LocalTraceMemory,
)

program_memory = LocalProgramMemory(
    index_name="my_program_memory",
)

document_memory = LocalDocumentMemory(
    index_name="my_document_memory",
)

fact_memory = LocalFactMemory(
    index_name="my_fact_memory",
)

trace_memory = LocalTraceMemory(
    index_name="my_trace_memory",
)
```