## RedisGraph schema
### Labels:
- Control: Represents a control point (start or end of the program).
- Action: Represents a document.
- Decision: Represents a chunk of content.
- Program: Represents a sub-program.

### Properties:
- Control:
  - name: The name of the control point (Start or End).
- Action:
  - name: The purpose of the action.
  - tool: The tool to use.
  - params: The prompt used to infer the parameters of the tool.
- Decision:
  - name: The question to ask.
  - purpose: The purpose of the decision.
- Program:
  - name: The index of the program within the graph memory.

### Relationship types:
- NEXT: Represents the sequential order of actions and decision
+ Any other needed by the decision making process
