

The `AskUser` Tool is usefull to ask information to the user and 

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
    lm = 
)
```

### Integrate it with Gradio

TODO