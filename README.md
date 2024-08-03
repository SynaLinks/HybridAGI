# HybridAGI: for people who want AI to behave as expected
## The programmable Cypher-oriented neuro-symbolic AGI

### Programming the future one node at a time

<div align="center">

[![Downloads](https://static.pepy.tech/badge/hybridagi/month)](https://pepy.tech/project/hybridagi)
[![Python package](https://github.com/SynaLinks/HybridAGI/actions/workflows/python-package.yaml/badge.svg)](https://github.com/SynaLinks/HybridAGI/actions/workflows/python-package.yaml)
![Beta](https://img.shields.io/badge/Release-Beta-blue)
[![License: GPL-3.0](https://img.shields.io/badge/License-GPL-green.svg)](https://opensource.org/license/gpl-3-0/)

</div>

**Disclaimer:** We are currently refactoring the project for better modularity and better ease of use. The FalkorDB integration will be done at the end of this refactoring. At that time we will accept contributions for the integration of other graph databases. For more information, join the Discord channel.

## Notebooks

## What is HybridAGI?

HybridAGI is the first (self)programmable LLM-based Agent that enables you to define its behavior using a **graph-based prompt programming** approach. Unlike other frameworks that view agents as advanced chatbots, we have adopted a methodology that is rooted in computer science, cognitive sciences, and symbolic AI.

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

**No React Agents here**, the only agent system that we provide is our unique and innovative **Graph Interpreter Agent** that follow a strict methodology by executing node by node the graph programs it have in memory. Because we control the behavior of the Agent from end-to-end by offloading planning to symbolic components, we can correct/enhance the behavior of the system easely, removing the needs for finetuning but also allowing the system to learn on the fly.

HybridAGI is build upon years of experience in making reliable robotics systems. We have combined our knowledge in Robotics, Symbolic AI, LLMs and Cognitive Sciences into a product for programmers, data-scientists and AI engineers. The long-term memory of our Agent system heavily use graphs to store structured and unstructured knowledge as well as its graph programs.

We provide everything for you to build your LLM application with a focus around Cypher Graph databases. We provide also a local database for rapid prototyping before scaling your application with one of our integration.

### Predictable/Deterministic behavior and infinite number of tools

Because we don't let the Agent choose the sequence of tools to use, we can use an infinite number of tools. By following the Graph Programs, we ensure a predictable and deterministic methodology for our Agent system. We can combine every memory system into one unique Agent by using the corresponding tools without limitation.

```python
import hybridagi.core.graph_program as gp

main = gp.GraphProgram(
    name="main",
    description="The main program",
)
    
main.add(gp.Decision(
    id="is_objective_unclear",
    purpose="Check if the Objective's is unclear",
    question="Is the Objective's question unclear?",
))

main.add(gp.Action(
    id="clarify",
    purpose="Ask one question to clarify the user's Objective",
    tool="AskUser",
    prompt="Please pick one question to clarify the Objective's question",
))

main.add(gp.Action(
    id="answer",
    purpose="Answer the question",
    tool="Speak",
    prompt="Please answer to the Objective's question",
))
    
main.add(gp.Action(
    id="refine_objective",
    purpose="Refine the objective",
    tool="UpdateObjective",
    prompt="Please refine the user Objective",
))
    
main.connect("start", "is_objective_unclear")
main.connect("is_objective_unclear", "clarify", label="Clarify")
main.connect("is_objective_unclear", "answer", label="Answer")
main.connect("clarify", "refine_objective")
main.connect("refine_objective", "answer")
main.connect("answer", "end")

main.build() # Verify the structure of the program

print(main)
# // @desc: The main program
# CREATE
# // Nodes declaration
# (start:Control {id: "start"}),
# (end:Control {id: "end"}),
# (is_objective_unclear:Decision {
#   id: "is_objective_unclear",
#   purpose: "Check if the Objective's is unclear",
#   question: "Is the Objective's question unclear?"
# }),
# (clarify:Action {
#   id: "clarify",
#   purpose: "Ask one question to clarify the user's Objective",
#   tool: "AskUser",
#   prompt: "Please pick one question to clarify the Objective's question"
# }),
# (answer:Action {
#   id: "answer",
#   purpose: "Answer the question",
#   tool: "Speak",
#   prompt: "Please answer to the Objective's question"
# }),
# (refine_objective:Action {
#   id: "refine_objective",
#   purpose: "Refine the objective",
#   tool: "UpdateObjective",
#   prompt: "Please refine the user Objective"
# }),
# // Structure declaration
# (start)-[:NEXT]->(is_objective_unclear),
# (is_objective_unclear)-[:CLARIFY]->(clarify),
# (is_objective_unclear)-[:ANSWER]->(answer),
# (clarify)-[:NEXT]->(refine_objective),
# (answer)-[:NEXT]->(end),
# (refine_objective)-[:NEXT]->(answer)
```

### Modular Pipelines

With HybridAGI you can build data extraction pipelines, RAG applications or advanced Agent systems, each being possibly optimized by using DSPy optimizers. We also provide pre-made modules and metrics for easy prototyping.

Each module and data type is *strictly typed and use Pydantic* as data validation layer. You can build pipelines in no time by stacking Modules sequentially like in Keras or HuggingFace.

```python
from hybridagi.embeddings import SentenceTransformerEmbeddings
from hybridagi.readers import PDFReader
from hybridagi.core.pipeline import Pipeline
from hybridagi.modules.splitters import DocumentSentenceSplitter
from hybridagi.modules.embedders import DocumentEmbedder

embeddings = SentenceTransformerEmbeddings(
    model_name_or_path = "all-MiniLM-L6-v2",
    dim = 384, # The dimention of the embeddings vector
)

reader = PDFReader()
input_docs = reader("data/SpelkeKinzlerCoreKnowledge.pdf") # This is going to extract 1 document per page

# Now that we have our input documents, we can start to make our data processing pipeline

pipeline = Pipeline()

pipeline.add("chunk_documents", DocumentSentenceSplitter())
pipeline.add("embed_chunks", DocumentEmbedder(embeddings=embeddings))

output_docs = pipeline(input_docs)
```

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
| `DocumentSearch` | Used to search for information into the document memory |
| `PastActionSearch` | Used to search for past actions into the trace memory |
| `GraphProgramSearch` | Used to search for graph programs into the program memory |
| `EntitySearch` | Used to search for entities into the fact memory |
| `FactSearch` | Used to search for facts into the fact memory |
| `QueryFacts` | Used to query facts from the fact memory |

</div>

<!-- ### Adding more tools

You can easely add more tools by using the `FunctionTool` and python functions like nowadays function calling.

```python
from hybridagi.modules.agents.tools import FunctionTool

def my_awesome_tool(foo: str):
    """
    The instructions to infer the tools parameters, this is going to be used in DSPy Signature
    """
    print(foo)
    # You should return a dictionary (usually containing the tool input + observation)
    return {"message": foo}

tool = FunctionTool(
    name = "AwesomeTool",
    func = my_awesome_tool,
)

``` -->

### Differences with LangGraph/LangChain or Llama-Index

We focus on **explainable and robust** systems, we don't support ReACT Agents that lack control and efficiency. We also provide everything to scale your application into production by offering optimizable pipelines, agents and graph databases integrations. Our system is a memory-centric agent with a special care to the long-term memory. Moreover our codebase is **readable, clean and elegant** we didn't over-engineer our system to obfuscate it or sell other services.

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

In contrast, programming each reasoning step demands expert knowledge in prompt engineering and programming. Surprisingly, it's enjoyable and not that difficult for programmers, you'll gain insight into how AI truly operates by controlling it, beeing able to enhance the sequence of action and decision. Natural language combined with algorithms opens up endless possibilities. We can't envision a world without it.