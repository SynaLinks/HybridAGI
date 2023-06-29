# What are Hybrid AGI graph programs ?

Let's dive into Hybrid AGI powerfull programs !

## Introducing Graph-Of-Prompt

While Large Language Models excel at generating text, they often lack logic and reasoning abilities. Hybrid architectures come to the rescue by bridging this gap. Although previous methods like Tree-Of-Prompt have shown effectiveness, they can be costly, slow, and not always relevant. In the following paragraphs, we introduce the concept of Generalized Decision and Action Graphs. These graphs can be viewed as cognitive programs that make probabilistic decisions and dictate the behavior of HybridAGI. This remarkable feature, called Graph-Of-Prompt, empowers the system to follow Turing complete programs composed of prompts to use external tools.

## Graph oriented prompt programming

Thanks to the design choices of HybridAGI programming, shaping its behavior is as simple as editing a `.cypher` file.

Programs are Cypher files that contain a property graph representing a cognitive program.

This program is a property graph with the following schema.

## Graph Program schema
### Labels:
- Control: Represents a control point (start or end of the program).
- Action: Represents an action (the use of a tool).
- Decision: Represents a decision.
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
- And any other needed by the decision making process

## Decisions

Decisions are a type of node that facilitate making choices. The options for a decision are represented by the outgoing edges of the decision node. You can use various options such as the classic YES/NO, add a MAYBE, or use it for multi classification. The limit is your imagination.

The output of a decision-making process is the next node to evaluate, based on the decision made. This enables AGI to follow logical paths within its program. Decisions can be used as conditional loops.

## Actions

Actions are a type of node that involve the use of tools by the Agent. The choice of the tool and its purpose is defined by the user in the program, while the tool's parameters are inferred from the prompt.

## Understanding limitations

The main limitation of this approach is that the working memory is constrained by the maximum size of the prompt. Therefore, efficient handling of complex tasks relies on the ability to save and retrieve information.

# Your first program

Here is the minimal backbone for coding a graph program:

```do_nothing.cypher
CREATE
(start:Control {name:"Start"}), // The starting point of the program
(end:Control {name:"End"}), // The ending point of the program
(start)-[:NEXT]->(end) // The end follow the start => do nothing
```

This program contains only the starting point and ending point, but do nothing, now let's add an action:

```hello_world.cypher
CREATE
(start:Control {name:"Start"}),
// We add a simple action
(say_hello:Action {name:"Greet the User", tool:"Speak", params:"Say hello in {language}\nSpeak:"}),
(end:Control {name:"End"}), 
(start)-[:NEXT]->(say_hello),
(say_hello)-[:NEXT]->(end)
```

Now we can experiment with decisions:

```clarify_objective.cypher
CREATE
(start:Control {name:"Start"}),
(ask_question:Action {name:"Ask question to clarify the objective", tool:"AskUser", params:"Pick one question to clarify the objective and ask it in {language}\nQuestion:"}),
(is_anything_unclear:Decision {name:"Is there anything unclear in the objective?", purpose:"Find out if there is anything unclear in the objective."}),
(end:Control {name:"End"}),
(start)-[:NEXT]->(ask_question),
(ask_question)-[:NEXT]->(is_anything_unclear),
(is_anything_unclear)-[:YES]->(ask_question),
(is_anything_unclear)-[:NO]->(end)
```

To enhance this program, we can use prompting techniques like the famous "Let's think in a step by step way" or add more option to the decision process to better take into account uncertainty:

```clarify_objective.cypher
CREATE
(start:Control {name:"Start"}),
(ask_question:Action {name:"Ask question to clarify the objective", tool:"AskUser", params:"Pick one question to clarify the objective and ask it in {language}\nQuestion:"}),
(is_anything_unclear:Decision {name:"Is there anything unclear in the objective?", purpose:"Find out if there is anything unclear in the objective. Let's think this out in a step by step way to be sure we have the right answer."}),
(clarify:Action {name:"Clarify the given objective", tool:"Predict", params:"The clarified objective.\Objective:"}),
(end:Control {name:"End"}),
(start)-[:NEXT]->(ask_question),
(ask_question)-[:NEXT]->(is_anything_unclear),
(is_anything_unclear)-[:MAYBE]->(ask_question),
(is_anything_unclear)-[:YES]->(ask_question),
(is_anything_unclear)-[:NO]->(clarify),
(clarify)-[:NEXT]->(end)
```

Finally we can use this behavior inside other programs using sub-programs:

```main.cypher
CREATE
(start:Control {name:"Start"}),
(clarify_objective:Program {name:"program:clarify_objective"}),
(end:Control {name:"End"}),
(start)-[:NEXT]->(clarify_objective),
(clarify_objective)-[:NEXT]->(end)
```

Now that you understand the basics, let's start !