

The `AskUser` Tool is usefull to ask information to the user during the execution of the program, to ask for confirmation or help for example.

## Output

```python



```

## Usage

```python

ask_user = AskUserTool(
    name = "AskUser" # The name of the tool
    agent_state = agent_state, # The state of the agent
    simulated = True, # Weither or not to simulate the user using a LLM
    func = None, # Callable function to integrate with front-end (optional)
    lm = None # The language model to use if different from the one configured (optional, default to None)
)

```