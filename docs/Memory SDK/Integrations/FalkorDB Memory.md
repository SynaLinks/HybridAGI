# FalkorDB Document Memory

## Usage

Before anything else, you will need to launch FalkorDB, the easiest way is using [Docker](https://www.docker.com/) with the following command:

```bash
docker run -p 6379:6379 -p 3000:3000 -it --rm falkordb/falkordb:latest
```

For more information about FalkorDB regarding persistance or security, please check their [documentation](https://docs.falkordb.com/).

Then you can instantiate your memory in your python code like in the following:

```python
from hybridagi.memory.integration.falkordb import (
    FalkorDBProgramMemory,
    FalkorDBDocumentMemory,
    FalkorDBFactMemory,
    FalkorDBTraceMemory,
)

program_memory = FalkorDBProgramMemory(
    index_name="my_program_memory",
    wipe_on_start=True,
)

document_memory = FalkorDBDocumentMemory(
    index_name="my_document_memory",
    wipe_on_start=True,
)

fact_memory = FalkorDBFactMemory(
    index_name="my_fact_memory",
    wipe_on_start=True,
)

trace_memory = FalkorDBTraceMemory(
    index_name="my_trace_memory",
    wipe_on_start=True,
)
```