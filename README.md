# HybridAGI: The Programmable Neuro-Symbolic AGI for people who want AI to behave as expected
![Beta](https://img.shields.io/badge/Release-Beta-blue)
[![License: GPL-3.0](https://img.shields.io/badge/License-GPL-green.svg)](https://opensource.org/license/gpl-3-0/)
[![Documentation](https://img.shields.io/badge/Docs-Documentation-blue)](https://synalinks.github.io/documentation)
---
[![Discord](https://dcbadge.vercel.app/api/server/82nt97uXcM)](https://discord.gg/82nt97uXcM)

HybridAGI is the *first Programmable LLM-based Autonomous Agent* that lets you program its behavior using a **graph-based prompt programming** approach. This state-of-the-art feature allows the AGI to efficiently use any tool while controlling the long-term behavior of the agent.

Become the *first Prompt Programmers in history*; be a part of the AI revolution one node at a time!

**Disclaimer: We are currently in the process of upgrading the codebase to integrate DSPy**

## Key Features 🎉

- **Automatic prompt optimization & finetuning:** Thanks to the integration of [DSPy](https://dspy-docs.vercel.app), HybridAGI can self-refine its own prompt automatically. This new feature helps the system optimize itself based on the examples you provide. You can use the LLM as a judge and train your AI with ease or even finetuning it. See the [examples](examples) for more information.

- **For AI makers:** This framework is intended for data scientists, prompt engineers, researchers, and AI enthusiasts who love to experiment with AI. This product requires some programming and prompt engineering knowledge to get the best out of it. It's a Build Yourself product where the focus is on human creativity rather than AI autonomy. If you are new to prompt engineering, start by looking at [this guide](https://www.promptingguide.ai/).

- **Memory-Centric AGI:** Thanks to a hybrid vector and graph database powered by [FalkorDB](https://www.falkordb.com/) enabling efficient storage of data, you can inspect its long-term memory and know what's going on at a glance! The AGI remembers its programs, can execute, or modify them dynamically.

- **Graph-based Prompt Programming:** HybridAGI allows you to encode its behavior using programs represented as graphs. This capability, at the core of our approach, ensures that the system follows a structured and logical behavior enabling conditional loops and multi-output decisions. Want to adapt its behavior to your workflow? [Learn how to program HybridAGI](https://synalinks.github.io/documentation/basics/graph-prompt-programming) using [Cypher](https://en.wikipedia.org/wiki/Cypher_(query_language))!

- **Graph Program Interpreter:** We introduce a revolutionary [LLM Agent as Graph Interpreter](hybridagi/agents/interpreter.py) that leverages probabilistic decision-making and graphs to determine actions based on a program. By reducing ambiguity and allowing composition of programs, this state-of-the-art feature enables the AGI to handle complex tasks with ease and precision.

- **One Prompt At a Time:** Our interpreter focuses on the current node's prompt to predict tool input, eliminating role confusion. This allows for seamless integration of multiple role-based prompts in the same program, enhancing flexibility, adaptability, and performance.

- **Use Open-Source Models:** HybridAGI's symbolic system offloads planning capabilities, enabling the use of smaller open-source LLM models. This results in a cost-effective, faster, and more sustainable solution. Guide the reasoning process of your agents efficiently and create better ones with fewer resources.

- **Free Software:** HybridAGI is a community-driven project, fostering collaboration, innovation, and shared ownership. The software is released under the GNU GPL license, inviting contributions from a diverse range of users and empowering the collective intelligence of the community. Its architecture allows you to *release your Cypher programs under the **license of your choice*** while using the framework under GNU GPL.

- **Do it Yourself:** The drawback to offloading the Agent planning capabilities to the symbolic components means that you have to build the algorithm yourself. Sure, you can emulate a React/MKRL Agent with a conditional loop and a decision... but where is the fun in that? You can find better, more specific to your use case, and more performant!

Many people think prompt engineering is an already dead discipline. The truth is that it's just the beginning of the journey; we have only scratched the surface of what is possible. Our product, HybridAGI, opens up new possibilities by making it possible to build entire conversational applications using prompt programs only, so you can focus on what matters:

*✨Finding the best prompt algorithm to fit your use case and quickly create AI that **behave as expected**✨*

## The Domain Specific Language (DSL) of HybridAGI

Like any programming language, it starts with a main prompt program...

main.cypher:
```javascript
// Nodes declaration
CREATE
(start:Control {name:"Start"}),
(end:Control {name:"End"}),
(answer:Action {
    name:"Answer the objective's question",
    tool:"Speak",
    prompt:"Answer the objective's question"
}),
// Structure declaration
(start)-[:NEXT]->(answer),
(answer)-[:NEXT]->(end)
```

You can also describe conditional loops or multi-output choices using decision nodes!

clarify_objective.cypher:
```javascript
// @desc: Clarify the objective if needed
CREATE
// Nodes declaration
(start:Control {name:"Start"}),
(end:Control {name:"End"}),
(is_anything_unclear:Decision {
    name:"Find out if there is anything unclear in the Objective", 
    question:"Is the Objective unclear?"
}),
(ask_question:Action {
    name:"Ask question to clarify the objective",
    tool:"AskUser",
    prompt:"Pick one question to clarify the Objective"
}),
(refine_objective:Action {
    name:"Clarify the given objective",
    tool:"UpdateObjective", 
    prompt:"The refined Objective"
}),
// Structure declaration
(start)-[:NEXT]->(is_anything_unclear),
(ask_question)-[:NEXT]->(refine_objective),
(refine_objective)-[:NEXT]->(is_anything_unclear),
// The outgoing edges of decision nodes give
// the possible answers to the system
(is_anything_unclear)-[:YES]->(ask_question),
// Decisions can have multiple arbitrary outcomes
(is_anything_unclear)-[:MAYBE]->(ask_question),
(is_anything_unclear)-[:NO]->(end)
```

And obvisouly, you can call other programs using Program nodes!

main.cypher:
```javascript
// Nodes declaration
CREATE
(start:Control {name:"Start"}),
(end:Control {name:"End"}),
(clarify_objective:Program {
    name:"Clarify the objective if needed",
    program:"clarify_objective"
}),
(answer:Action {
    name:"Answer the objective's question",
    tool:"Speak",
    prompt:"Answer the objective's question"
}),
// Structure declaration
(start)-[:NEXT]->(clarify_objective),
(clarify_objective)-[:NEXT]->(answer),
(answer)-[:NEXT]->(end)
```

Here is a trace of the above example, the system can simulate user input to optimize/finetune itself without human intervention.

```
 --- Step 0 ---
Call Program: main
Program Purpose: What's the meaning of life?
 --- Step 1 ---
Call Program: clarify_objective
Program Purpose: Clarify the objective if needed
 --- Step 2 ---
Decision Purpose: Find out if there is anything unclear in the Objective
Decision Question: Is the Objective unclear?
Decision: MAYBE
 --- Step 3 ---
Action Purpose: Ask question to clarify the objective
Action: {
  "question": "Do you mean to ask about the philosophical or personal significance of life in general, or are you asking for guidance on finding personal fulfillment and satisfaction?",
  "answer": "I believe in seeking personal growth and happiness. For me, the meaning of life could be finding joy in relationships, pursuing passions, and making a positive impact on the world. However, this question is deeply philosophical and can have many interpretations."
}
 --- Step 4 ---
Action Purpose: Clarify the given objective
Action: {
  "new_objective": "New Objective: Which aspects of personal growth, relationships, passions, and making a positive impact on the world should I focus on to find meaning and satisfaction in my life?",
  "observation": "Successfully updated"
}
 --- Step 5 ---
Decision Purpose: Find out if there is anything unclear in the Objective
Decision Question: Is the Objective unclear?
Decision: NO
 --- Step 6 ---
End Program: clarify_objective
 --- Step 7 ---
Action Purpose: Answer the objective's question
Action: {
  "message": "To find meaning and satisfaction in your life, consider focusing on various aspects of personal growth, relationships, passions, and making a positive impact on the world. Here are some suggestions for each area:\n\n1. Personal Growth: Continuously learn new skills, read books, travel, practice mindfulness, set goals, and engage in activities that challenge you and help you grow as an individual.\n2. Relationships: Nurture your existing relationships by actively listening, expressing gratitude, and showing empathy. Build new connections through networking, joining clubs or groups, and volunteering.\n3. Passions: Pursue hobbies or activities that bring you joy and fulfillment. Dedicate time to these passions regularly, and consider sharing them with others to expand your network and learn from their experiences.\n4. Making a Positive Impact on the World: Identify causes or issues that resonate with you and find ways to contribute to them. Volunteer, donate, spread awareness, or engage in activism. Remember that even small actions can make a significant difference.\n\nFeel free to ask any questions or clarifications regarding this response."
}
 --- Step 8 ---
End Program: main
```

HybridAGI output the chat history, along with the final answer and trace allowing DSPy to optimize every aspect of a conversational agent: the result, the intermediary steps but also the interaction with the user.

Chat History:
```
[
  {
    "role": "User",
    "message": "What's the meaning of life?"
  },
  {
    "role": "AI",
    "message": "Do you mean to ask about the philosophical or personal significance of life in general, or are you asking for guidance on finding personal fulfillment and satisfaction?"
  },
  {
    "role": "User",
    "message": "I believe in seeking personal growth and happiness. For me, the meaning of life could be finding joy in relationships, pursuing passions, and making a positive impact on the world. However, this question is deeply philosophical and can have many interpretations."
  },
  {
    "role": "AI",
    "message": "To find meaning and satisfaction in your life, consider focusing on various aspects of personal growth, relationships, passions, and making a positive impact on the world. Here are some suggestions for each area:\n\n1. Personal Growth: Continuously learn new skills, read books, travel, practice mindfulness, set goals, and engage in activities that challenge you and help you grow as an individual.\n2. Relationships: Nurture your existing relationships by actively listening, expressing gratitude, and showing empathy. Build new connections through networking, joining clubs or groups, and volunteering.\n3. Passions: Pursue hobbies or activities that bring you joy and fulfillment. Dedicate time to these passions regularly, and consider sharing them with others to expand your network and learn from their experiences.\n4. Making a Positive Impact on the World: Identify causes or issues that resonate with you and find ways to contribute to them. Volunteer, donate, spread awareness, or engage in activism. Remember that even small actions can make a significant difference.\n\nFeel free to ask any questions or clarifications regarding this response."
  }
]
```

Many more systems are possible, interactive or non-interactive ones, this is just a glimpse into the future! Look at the [examples](examples) for more inspiration.

Learn more about Graph-based Prompt Programming by reading our [documentation](https://synalinks.github.io/documentation/basics/graph-prompt-programming).

### Install

```bash
git clone https://github.com/SynaLinks/HybridAGI.git
cd HybridAGI
virtualenv venv
source venv/bin/activate
pip install poetry
poetry install
```

### Setup the Knowledge Base

Then setup the knowledge base & sandbox using docker:

```
docker compose up
```

Open your browser at `http://localhost:8001` and connect to an existing database with the hostname `hybrid-agi-db` and port `6379`.

### Run the tests

Use the following command to run the tests:

```
poetry run pytest -vv
```

# FAQ

### What do you mean by neuro-symbolic AGI?

We believe that agent systems are the future of general artificial intelligence and robotics. Our goal is to build an agent system that solves real-world problems by using an intermediary language interpretable by both humans and machines. If we want to keep humans in the loop in the coming years, we need to design AI systems for that purpose. Coming from a robotic background, we understand how the debate in the ML community between multi-agent systems and neuro-symbolic ones will unfold.

### How is HybridAGI different from a toolbox?

Our aim is to develop an entire ecosystem around our technology. Like an autonomous car is composed of several sub-systems, robotic softwares are composed by different and complementary sub-systems coordinating themselves. With neuro-symbolic systems, you need to train your neural networks with the whole architecture to increase efficiency by taking into account the contraints and new knowledge created by this neuro-symbolic architecture. We plan to release soon small finetuned models to allow the system to accuratly navigate into the graph and with programming knowledge about our DSL to enable long-term planning agent. By lowering the costs of long-term agent workers, we enable new usecases for the entire industry.

### What is the difference between LangGraph and HybridAGI?

LangGraph, being a Python low-code framework, it is actually more complex to build a system with. Cypher, on the other hand, is designed to be easy for people to understand at a glance. More importantly, our DSL is designed to allow LLMs to read, write, and modify it on the fly without any prior training, enabling programs with self-healing or self-programming capability just to name a few. The graphs fit into a prompt and are semantically separated like code, requiring only 4 node types to describe the system of your choice. Additionally, automatic prompt optimization and fine-tuning are leveraged to their maximum capability by focusing solely on DSPy and removing LangChain from our codebase.

### What is the benefit of using HybridAGI over DSPy with Llama-index?

HybridAGI is specifically tailored for building interactive and reasoning agents quickly and effortlessly. The DSL allows for algorithmic flexibility while making it possible to describe every type of system without having to implement it from scratch. Plus, we focus our work on an open-source vector/graph database, allowing people and businesses to maintain control of their data.

### How does HybridAGI help me regarding the EU AI Act or future regulation on your country for non-EU?

Because this system can only execute actions that are in the graph, businesses can use the graph to classify the behavior of their AI system and document it. However, this is not sufficient, and you should always conduct specific safety tests in accordance with the safety practices of your domain, in particular red-teaming of the model. We plan to release tools to help regarding these aspects.

### Can HybridAGI be used for tasks other than robotics?

Yes, HybridAGI can be used for a wide range of tasks beyond robotics. The system is designed to be flexible and adaptable, making it suitable for any application that requires complex reasoning and decision-making, such as retrieval-augmented generation (RAG), chatbots, knowledge scrapers, personal assistant, and more generally, any agent-based application.

### How can I contribute to HybridAGI?

We encourage you to join our community on Discord to connect with other developers and share your ideas.

## Credits 👏

HybridAGI is made possible by the following open-source tools:

- [DSPy](https://dspy-docs.vercel.app/) framework
- [FalkorDB](https://www.falkordb.com/) database

## Contributors 🔥

<a href="https://github.com/SynaLinks/HybridAGI/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=SynaLinks/HybridAGI" />
</a>

## Cite this work

If you found this repository usefull for your research, please consider citing us:

```bibtex
@misc{Sallami2023,
  author = {Yoan Sallami},
  title = {HybridAGI: Introducing graph-based prompt programming},
  year = {2023},
  publisher = {GitHub},
  journal = {GitHub repository},
  howpublished = {\url{https://github.com/SynaLinks/HybridAGI}}
}
```

## Get Involved 💬
[![Discord](https://dcbadge.vercel.app/api/server/82nt97uXcM)](https://discord.gg/82nt97uXcM)

Become a part of our community of developers, researchers, and AI enthusiasts. Contribute to the project, share your feedback, and help shape the future of Hybrid AGI. We welcome and value your participation!

## Who we are? 🔥

We're not based in Silicon Valley or part of a big company; we're a small, dedicated team from the south of France. Our focus is on delivering an AI product where the user maintains control. We're dissatisfied with the current trajectory of Agent-based products. We are expert in human-robot interaction and building interactive systems that behave as expected. While we draw inspiration from cognitive sciences and symbolic AI, we aim to keep our concepts grounded in computer science for a wider audience.

Our mission extends beyond AI safety and performance; it's about shaping the world we want to live in. Even if programming becomes obsolete in 5 or 10 years, replaced by some magical prompt, we believe that traditional prompts are insufficient for preserving jobs. They're too simplistic and fail to accurately convey intentions.

In contrast, programming each reasoning step demands expert knowledge in prompt engineering and programming. Surprisingly, it's enjoyable and not that difficult for programmers, you'll gain insight into how AI truly operates by controlling it, beeing able to enhance the sequence of action and decision. Natural language combined with algorithms opens up endless possibilities. We can't envision a world without it.

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=SynaLinks/HybridAGI&type=Date)](https://star-history.com/#SynaLinks/HybridAGI&Date)