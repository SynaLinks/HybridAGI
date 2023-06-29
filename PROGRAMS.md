## Harnessing the Power of Hybrid AGI with Graph Programs

Welcome to the world of Hybrid AGI graph programs! In this exciting realm, we combine the strengths of Large Language Models with the logic and reasoning abilities of graph-based architectures. By leveraging the concept of Generalized Decision and Action Graphs, we empower Hybrid AGI to follow Turing complete programs composed of prompts and external tools. Let's explore this fascinating topic further!

### Introducing Hybrid AGI Graph Programs

Hybrid AGI graph programs are cognitive programs represented as property graphs, which serve as a guiding structure for the behavior of the system. These programs consist of nodes and relationships that dictate the sequence of actions, decisions, and sub-programs to be executed. By leveraging the Graph-Of-Prompt paradigm, Hybrid AGI gains the ability to make probabilistic decisions and utilize external tools effectively.

### The Graph Program Schema

To design and understand Hybrid AGI graph programs, let's explore the schema used in these programs:

#### Labels:

- Control: Represents a control point, such as the start or end of the program.
- Action: Represents an action involving the use of a tool.
- Decision: Represents a decision-making point.
- Program: Represents a sub-program within the graph memory.

#### Properties:

- Control:
  - name: The name of the control point (Start or End).
- Action:
  - name: The purpose of the action.
  - tool: The tool to use for executing the action.
  - params: The prompt used to infer the parameters of the tool.
- Decision:
  - name: The question to ask or the decision to be made.
  - purpose: The purpose of the decision.
- Program:
  - name: The index of the program within the graph memory.

#### Relationship types:

- NEXT: Represents the sequential order of actions and decisions.
- And any other relationship types needed by the decision-making process.

### Decisions in Graph Programs

Decisions play a crucial role in Hybrid AGI graph programs by facilitating choices and branching paths. Each decision node offers options represented by outgoing edges, enabling diverse possibilities for decision-making. Whether it's a classic YES/NO scenario, a multi-classification choice, or even adding a MAYBE option, decisions provide the flexibility for AGI to follow logical paths within its program. Decisions can also be utilized as conditional loops, allowing for iterative processes and adaptive behavior.

### Actions in Graph Programs

Actions in Hybrid AGI graph programs involve the use of tools by the agent. The choice of the tool and its purpose is defined within the program itself, while the parameters of the tool are inferred from the prompt. By incorporating various actions, Hybrid AGI gains the capability to interact with external systems and perform specific tasks.

### Understanding Limitations

While Hybrid AGI graph programs offer powerful capabilities, it's important to consider their limitations. One such limitation arises from the maximum size constraint of the prompt, which impacts the working memory of the system. Handling complex tasks efficiently requires the ability to save and retrieve information effectively.

### Your First Graph Program

To get started with Hybrid AGI graph programming, let's dive into your first program! Below is a minimal example that demonstrates the backbone of a graph program:

```do_nothing.cypher
CREATE
(start:Control {name: "Start"}),  // The starting point of the program
(end:Control {name: "End"}),      // The ending point of the program
(start)-[:NEXT]->(end)            // The end follows the start, resulting in no action
```

In this program, we have only defined the starting point and ending point, effectively doing nothing. Let's now enhance the program by adding an action:

```hello_world.cypher
CREATE
(start:Control {name: "Start"}),
(say_hello:Action {name: "Greet the User", tool: "Speak", params: "Say hello in {language}\nSpeak:"}),
(end:Control {name: "End"}),
(start)-[:NEXT]->(say_hello),
(say_hello)-[:NEXT]->(end)
```

In the updated program, we have introduced an action called "Greet the User" utilizing the "Speak" tool. The parameters for this action are inferred from the prompt, allowing AGI to greet the user in their preferred language.

To further enhance the program, we can incorporate decision-making:

```clarify_objective.cypher
CREATE
(start:Control {name: "Start"}),
(ask_question:Action {name: "Ask question to clarify the objective", tool: "AskUser", params: "Pick one question to clarify the objective and ask it in {language}\nQuestion:"}),
(is_anything_unclear:Decision {name: "Is there anything unclear in the objective?", purpose: "Find out if there is anything unclear in the objective."}),
(end:Control {name: "End"}),
(start)-[:NEXT]->(ask_question),
(ask_question)-[:NEXT]->(is_anything_unclear),
(is_anything_unclear)-[:YES]->(ask_question),
(is_anything_unclear)-[:NO]->(end)
```

In this program, we introduce a decision point to clarify the objective. If there is something unclear, the AGI will ask the user for clarification repeatedly until the objective is clear. Once the objective is clear, the program will proceed to the end.

To make the decision-making process more robust and consider uncertainty, we can use prompting techniques like "Let's think in a step-by-step way" or expand the options for decision outcomes:

```clarify_objective.cypher
CREATE
(start:Control {name: "Start"}),
(ask_question:Action {name: "Ask question to clarify the objective", tool: "AskUser", params: "Pick one question to clarify the objective and ask it in {language}\nQuestion:"}),
(is_anything_unclear:Decision {name: "Is there anything unclear in the objective?", purpose: "Find out if there is anything unclear in the objective. Let's think this out in a step-by-step way to be sure we have the right answer."}),
(clarify:Action {name: "Clarify the given objective", tool: "Predict", params: "The clarified objective.\Objective:"}),
(end:Control {name: "End"}),
(start)-[:NEXT]->(ask_question),
(ask_question)-[:NEXT]->(is_anything_unclear),
(is_anything_unclear)-[:MAYBE]->(ask_question),
(is_anything_unclear)-[:YES]->(ask_question),
(is_anything_unclear)-[:NO]->(clarify),
(clarify)-[:NEXT]->(end)
```

In this enhanced program, we incorporate the "step-by-step" thinking approach to ensure a clear objective. The decision node allows for a MAYBE option in addition to YES and NO, providing more flexibility in handling uncertainty. The clarified objective is then obtained through the "Predict" tool.

To utilize this behavior within other programs, we can create sub-programs:

```main.cypher
CREATE
(start:Control {name: "Start"}),
(clarify_objective:Program {name: "program:clarify_objective"}),
(end:Control {name: "End"}),
(start)-[:NEXT]->(clarify_objective),
(clarify_objective)-[:NEXT]->(end)
```

In this example, the main program incorporates the sub-program "clarify_objective." This modularity allows for the reuse and composition of different program components to achieve more complex behaviors.

Now that you have a solid understanding of Hybrid AGI graph programs, you're ready to dive deeper and unleash the power of graph-oriented prompt programming!