# QuickStart

Welcome to HybridAGI documentation, you will find the ressources to understand and program HybridAGI a programmable LLM based Agent system based on a custom [Domain Specific Language](https://en.wikipedia.org/wiki/Domain-specific_language) (DSL) based on [Cypher](https://en.wikipedia.org/wiki/Cypher_(query_language)), a popular graph database query language.

### LLM Agent as Graph VS LLM Agent as Graph Interpreter

What makes our approach different from Agent as Graph (like LangGraph or LLama-Index) is the fact that our Agent system is *not a static finite state machine*, but an interpreter that can read/write and execute node by node a *dynamic graph data* (the graph programs) structure separated from that process. Making possible for the Agent to learn by executing, reading and modifying the graph programs (like any other data), in its essence HybridAGI is intended to be a self-programming system centered around the Cypher language.

## Install

### With pip (recommended)

To install easily HybridAGI we recommend you to use pip with the following command:
```
pip install hybridagi
```

### From sources

If you want to explore more in depth our system, or contribute to the project, you can use the following command to install HybridAGI from sources:
```
git clone https://github.com/SynaLinks/HybridAGI
cd HybridAGI
pip install .
```

## Key Features

- **Correct the behavior of your Agent without any fine-tuning**: HybridAGI was designed from the ground up to be easily corrected on the fly, a required condition for continuous learning. By following a Graph Program encoding its behavior, the Agent solely execute the steps provided.

- **Turing Complete DSL**: HybridAGI's Turing Complete Domain Specific Language (DSL) has been specifically designed to describe an infinite number of algorithms using only 4 different types of nodes (Control, Action, Decision, Program). The interpreter Agent can loop and call subprograms, similar to a traditional programming language.

- **Graph Program Search & Dynamic Call**: Because our agent system is not a static finite state machine but an interpreter that interprets a graph-based DSL node by node, it can search programs into memory and dynamically call the best one to solve the user query. It can also learn new methodologies by creating new programs on the fly.

- **Optimizable Pipeline & Agent**: With HybridAGI and DSPy, you can optimize the data processing pipelines and the agent system to your own needs. Since each HybridAGI module is also a DSPy module, you can use DSPy optimizers seamlessly with them.

- **Agent Behavior as Software**: With HybridAGI, you can ship the Agent's behavior as Cypher software, enabling start-ups and companies to create their own IP based on their business logic implemented in Cypher.

- **Memory-Centric System**: HybridAGI is a memory-centric system that heavily uses Knowledge Graphs, both for executing programs and to store structured knowledge.

- **Secure and Safe**: Special attention has been given to prevent Cypher Injections but also to prevent the Agent system from modifying its own main prompting mechanism by introducing the concept of protected programs.