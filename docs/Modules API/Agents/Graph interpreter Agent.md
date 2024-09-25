# Graph Interpreter Agent

The `GraphInterpreterAgent` is the agent system that execute the Cypher software stored in memory, it can branch over the graph programs by asking itself question when encountering decision steps, and use tools when encountering an Action step and jump to other programs when encountering Program steps. 

## Usage

```python
from hybridagi.modules.agents import GraphInterpreterAgent
from hybridagi.core.datatypes import AgentState
from hybridagi.modules.agents.tools import PredictTool, SpeakTool

agent_state = AgentState()

tools = [
    PredictTool(),
    SpeakTool(
        agent_state = agent_state,
    )
]

agent = GraphInterpreterAgent(
    agent_state = agent_state, # The agent state
    program_memory = program_memory, # The program memory where the graph programs are stored 
    embeddings = None, # The embeddings to use when storing the agent steps (optional, default to None)
    trace_memory = None, # The trace memory to store the agent steps (optional, default to None)
    tools = tools, # The list of tools to use for the agent
    entrypoint = "main" # The entrypoint for the graph programs (default to main)
    num_history = 5, # The number of last steps to remember in the agent context (Default to 5)
    commit_decision_steps = False, # Weither or not to use the decision steps in the agent context (default to False)
    decision_lm = None, # The decision language model to use if different from the one configured (optional, default to None)
    verbose = True, # Weither or not to display the colorful trace when executing the program (default to True)
    debug = False, # Weither or not to raise exceptions during the execution of a program (default to False)
)

result = agent(Query(text="What is the capital of France?"))

```