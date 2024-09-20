# HybridAGI: for people who want AI to behave as expected
## The Programmable Cypher-based Neuro-Symbolic AGI

### Your All-In-One framework for interactive knowledge intensive LLM applications

<div align="center">

[![Downloads](https://static.pepy.tech/badge/hybridagi/month)](https://pepy.tech/project/hybridagi)
[![Python package](https://github.com/SynaLinks/HybridAGI/actions/workflows/python-package.yaml/badge.svg)](https://github.com/SynaLinks/HybridAGI/actions/workflows/python-package.yaml)
![Beta](https://img.shields.io/badge/Release-Beta-blue)
[![License: GPL-3.0](https://img.shields.io/badge/License-GPL-green.svg)](https://opensource.org/license/gpl-3-0/)

</div>

**Disclaimer:** We are currently refactoring the project for better modularity and better ease of use. For now, only the Local integration is available, the FalkorDB & Kuzu integration will be done at the end of this refactoring. At that time we will accept contributions for the integration of other Cypher-based graph databases. For more information, join the Discord channel.

## Key Features

- **Turing Complete DSL**: HybridAGI's Turing Complete Domain Specific Language (DSL) has been specifically designed to describe an infinite number of algorithms using only 4 different types of nodes (Control, Action, Decision, Program). The interpreter Agent can loop and call subprograms, similar to a traditional programming language.

- **Graph Program Search & Dynamic Call**: Because our agent system is not a static finite state machine but an interpreter that interprets a graph-based DSL node by node, it can search programs into memory and dynamically call the best one to solve the user query.

- **Optimizable Pipeline & Agent**: With HybridAGI and DSPy, you can optimize the data processing pipelines and the agent system to your own needs. Since each HybridAGI module is also a DSPy module, you can use DSPy optimizers seamlessly with them.

- **Agent Behavior as Software**: With HybridAGI, you can ship the Agent's behavior as Cypher software, enabling start-ups and companies to create their own IP based on their business logic implemented in Cypher.

- **Memory-Centric System**: HybridAGI is a memory-centric system that heavily uses Knowledge Graphs, both for executing programs and to store structured knowledge. This enables Knowledge Graph RAG applications for critical domains.

- **Secure and Safe**: Special attention has been given to prevent Cypher Injections but also to prevent the Agent system from modifying its own main prompting mechanism by introducing the concept of protected programs.

## Notebooks

- [Datatypes](notebooks/datatypes.ipynb)
- [GraphPrograms](notebooks/graph_programs.ipynb)
- [Interpreter Prompting](notebooks/interpreter_prompting.ipynb)
- [Simulating User](notebooks/simulating_user.ipynb)
- [Vector Only RAG](notebooks/vector_only_rag.ipynb)
- [Knowledge Graph RAG](notebooks/knowledge_graph_rag.ipynb)
- [Episodic RAG](notebooks/episodic_memory_rag.ipynb)
- [Extracting Knowledge Graphs](notebooks/extracting_knowledge_graphs.ipynb)
- [Dynamic Graph Program](notebooks/dynamic_graph_program.ipynb)
- [Using External Tools](notebooks/using_external_tools.ipynb)
- [Add Documents (on the fly)](notebooks/updating_documents.ipynb)
- [Add Facts (on the fly)](notebooks/updating_facts.ipynb)
- [Interactive ReACT](notebooks/interactive_react.ipynb)
- [ReACT Agent](notebooks/react_agent.ipynb)
- [Reflexion Agent](notebooks/reflexion_agent.ipynb)
- [Using FalkorDB](notebooks/using_falkordb.ipynb)

## What is HybridAGI?

HybridAGI is the first programmable LLM-based Agent that enables you to define its behavior using a **graph-based prompt programming** approach. Unlike other frameworks that view agents as advanced chatbots, we have adopted a methodology that is rooted in computer science, cognitive sciences, and symbolic AI.

To us, an agent system is an goal-directed cognitive software that can process natural language and execute the tasks it has been programmed to perform. Just like with traditional software, the developer specifies the behavior of the application, and the system is not truly autonomous unless it has been programmed to be so. Programming the system not only helps the agent to carry out its tasks but also allows for the *formalization of the developer's intent*.

HybridAGI is designed for data scientists, prompt engineers, researchers, and AI enthusiasts who love to experiment with AI. It is a "Build Yourself" product that focuses on human creativity rather than AI autonomy.

### Why HybridAGI?

We are not satisfied with the current trajectory of Agent-based systems that lack control and efficiency. Today's approach is to build React/MKRL agents that do what they want without any human control, resulting in infinite loops of nonsense because they tend to stay in their data distribution. Multi-agent systems try to solve that, but instead result in more nonsense and prohibitive costs due to the agents chitchatting with each other. Moreover, today's agents require fine-tuning to enhance/correct the behavior of the agent system. In contrast, with HybridAGI, the only thing you need to do is to modify the behavior graph (the graph programs).

We advocate that fine-tuning should be done only as a last resort when in-context learning fails to give you the expected result. Any person who has already fine-tuned a LLM knows that gathering data is hard, but having the right variability in your dataset is even harder, thus prohibiting most companies from leveraging this technology if they don't have many AI scientists. By rooting cognitive sciences into computer science concepts, without obfuscating them, we empower programmers to build the Agent system of their dreams by controlling the sequence of action and decision.

Our goal is to build an agent system that solves real-world problems by using an intermediary language interpretable by both humans and machines. If we want to keep humans in the loop in the coming years, we need to design Agent systems for that purpose.

### Install

```
pip install hybridagi
```

### Graphs for planning and knowledge management, no finetuning required.

**No React Agents here**, the only agent system that we provide is our custom **Graph Interpreter Agent** that follow a strict methodology by executing node by node the graph programs it have in memory. Because we control the behavior of the Agent from end-to-end by offloading planning to symbolic components, we can correct/enhance the behavior of the system easely, removing the needs for finetuning but also allowing the system to learn on the fly.

HybridAGI is build upon years of experience in making reliable Robotics systems. We have combined our knowledge in Robotics, Symbolic AI, LLMs and Cognitive Sciences into a product for programmers, data-scientists and AI engineers. The long-term memory of our Agent system heavily use graphs to store structured and unstructured knowledge as well as its graph programs.

We provide everything for you to build your LLM application with a focus around Cypher Graph databases. We provide also a local database for rapid prototyping before scaling your application with one of our integration.

<div align="center">

![pipeline](img/memories.png)

</div>

### Predictable/Deterministic behavior and infinite number of tools

Because we don't let the Agent choose the sequence of tools to use, we can use an infinite number of tools. By following the Graph Programs, we ensure a predictable and deterministic methodology for our Agent system. We can combine every memory system into one unique Agent by using the corresponding tools without limitation.

<div align="center">

![pipeline](img/graph_program.png)

</div>

### Modular Pipelines

With HybridAGI you can build data extraction pipelines, RAG applications or advanced Agent systems, each being possibly optimized by using DSPy optimizers. We also provide pre-made modules and metrics for easy prototyping.

Each module and data type is *strictly typed and use Pydantic* as data validation layer. You can build pipelines in no time by stacking Modules sequentially like in Keras or HuggingFace.

<div align="center">

![pipeline](img/pipeline.png)

</div>

### Native tools

We provide the following list of native tools to R/W into the memory system or modify the state of the agent:
<div align="center">

| Tool Name      | Usage      |
| -------------- | ------------- |
| `Predict`        | Used to populate the context with reasoning information |
| `ChainOfThought` | Used to populate the context with reasoning information |
| `Speak` | Used to send message to the User and give the final answer |
| `AskUser` | Used to ask question to the User (can simulate the user persona) |
| `UpdateObjective` | Update the long-term Objective of the Agent |
| `AddDocument` | Save into memory a new document |
| `AddFacts` | Save into memory new facts |
| `DocumentSearch` | Used to search for information into the document memory |
| `PastActionSearch` | Used to search for past actions into the trace memory |
| `EntitySearch` | Used to search for entities into the fact memory |
| `FactSearch` | Used to search for facts into the fact memory |
| `QueryFacts` | Used to query facts from the fact memory |
| `GraphProgramSearch` | Used to search for graph programs into the program memory |
| `ReadGraphProgram` | Used to read a graph program from memory by name |
| `CallGraphProgram` | Used to dynamically call a graph program from memory by name |

</div>

### Adding more tools

You can add more tools by using the `FunctionTool` and python functions like nowadays function calling.

<div align="center">

![pipeline](img/custom_tool.png)

</div>

### Graph Databases Integrations

- Local Graph Memory for rapid prototyping based on [NetworkX](https://networkx.org/).
- [FalkorDB](https://www.falkordb.com/) low latency in-memory hybrid vector/graph database.
- [Kuzu](https://kuzudb.com/) A highly scalable, extremely fast, easy-to-use embeddable graph database (coming soon).

We accept the contributions for more database integrations. Feel free to join the discord channel for more information!

### LLM Agent as Graph VS LLM Agent as Graph Interpreter

What makes our approach different from Agent as Graph is the fact that our Agent system is not a process represented by a graph, but an interpreter that can read/write and execute a graph data (the graph programs) structure separated from that process. Making possible for the Agent to learn by executing, reading and modifying the graph programs (like any other data), in its essence HybridAGI is intended to be a self-programming system centered around the Cypher language. It is a production-ready research project centered around neuro-symbolic programming, program synthesis and symbolic AI.

### Differences with LangGraph/LangChain or Llama-Index

We focus on **explainable and robust** systems, we don't support ReACT Agents that lack control and efficiency. The Agent system we provide, is custom made. We also provide everything to scale your application into production by offering optimizable pipelines, agents and graph databases integrations. Our system is a memory-centric agent with a special care to the long-term memory. Moreover our codebase is **readable, clean and elegant** we didn't over-engineer our system to obfuscate it to sell other services.

### Differences with DSPy

Unlike DSPy, our programs are not static but dynamic and can adapt to the user query by dynamically calling programs stored into memory. Moreover we focus our work on explainable neuro-symbolic AGI systems using Graphs. The graph programs are easier to build than implementing them from scratch using DSPy. If DSPy is the PyTorch of LLM applications, think of HybridAGI as the Keras or HuggingFace of neuro-symbolic LLM applications.

## Get Involved

[![Discord Channel](https://dcbadge.vercel.app/api/server/82nt97uXcM)](https://discord.gg/82nt97uXcM)

Become a part of our community of developers, researchers, and AI enthusiasts. Contribute to the project, share your feedback, and help shape the future of HybridAGI. We welcome and value your participation!

## Contributors

<a href="https://github.com/SynaLinks/HybridAGI/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=SynaLinks/HybridAGI" />
</a>

## Who we are?

We're not based in Silicon Valley or part of a big company; we're a small, dedicated team from the south of France. Our focus is on delivering an AI product where the user maintains control. We're dissatisfied with the current trajectory of Agent-based products. We are expert in human-robot interactions and building interactive systems that behave as expected. While we draw inspiration from cognitive sciences and symbolic AI, we aim to keep our concepts grounded in computer science for a wider audience.

Our mission extends beyond AI safety and performance; it's about shaping the world we want to live in. Even if programming becomes obsolete in 5 or 10 years, replaced by some magical prompt, we believe that traditional prompts are insufficient for preserving jobs. They're too simplistic and *fail to accurately convey intentions*.

In contrast, programming each reasoning step demands expert knowledge in prompt engineering and programming. Surprisingly, it's enjoyable and not that difficult for programmers, you'll gain insight into how AI truly operates by controlling it, being able to enhance the sequence of action and decision. Natural language combined with algorithms opens up endless possibilities. We can't envision a world without it.

## Commercial Usage

Our software is released under GNU GPL license to protect ourselves and the contributions of the community.
The logic of your application being separated (the graph programs) there is no IP problems for you to use HybridAGI. Moreover when used in production, you surely want to make a FastAPI server to request your agent and separate the backend and frontend of your app (like a website), so the GPL license doesn't contaminate the other pieces of your software.

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=SynaLinks/HybridAGI&type=Date)](https://star-history.com/#SynaLinks/HybridAGI&Date)
