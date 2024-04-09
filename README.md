# HybridAGI: The Programmable Neuro-Symbolic AGI for people who want AI to behave as expected
![Beta](https://img.shields.io/badge/Release-Beta-blue)
[![License: GPL-3.0](https://img.shields.io/badge/License-GPL-green.svg)](https://opensource.org/license/gpl-3-0/)
[![Documentation](https://img.shields.io/badge/Docs-Documentation-blue)](https://synalinks.github.io/documentation)
---

HybridAGI is the *first Programmable LLM-based Autonomous Agent* that lets you program its behavior using a **graph-based prompt programming** approach. This state-of-the-art feature allows the AGI to efficiently use any tool while controlling the long-term behavior of the agent.

Become the *first Prompt Programmers in history*; be a part of the AI revolution one node at a time!

**Disclaimer: We are currently in the process of upgrading the codebase to integrate DSPy**

## Key Features 🎉

- **🚀Automatic prompt optimization & finetuning:** Thanks to the integration of [DSPy](https://dspy-docs.vercel.app), HybridAGI can now self-refine its own prompt automatically. This new feature helps the system optimize itself based on the examples you provide. You can even use the LLM as a tutor and train your AI in a self-supervised fashion with ease or finetuning it. See the [examples](examples) for more information.

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

Learn more about Graph-based Prompt Programming by reading our [documentation](https://synalinks.github.io/documentation/basics/graph-prompt-programming).

### Install from pip

```bash
virtualenv venv
source venv/bin/activate
pip install git+https://github.com/SynaLinks/HybridAGI
```

### Install from source

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
cd HybridAGI
docker compose up
```

Open your browser at `http://localhost:8001` and connect to an existing database with the hostname `hybrid-agi-db` and port `6379`.

### Run the tests

Use the following command to run the tests:

```
poetry run pytest -vv
```

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
[![Discord](https://dcbadge.vercel.app/api/server/zM2rEfsqxj)](https://discord.gg/zM2rEfsqxj)

Become a part of our community of developers, researchers, and AI enthusiasts. Contribute to the project, share your feedback, and help shape the future of Hybrid AGI. We welcome and value your participation!

## Who we are? 🔥

We're not based in Silicon Valley or part of a big company; we're a small, dedicated team from the south of France. Our focus is on delivering an AI product where the user maintains control. We're dissatisfied with the current trajectory of Agent-based products. We are expert in human-robot interaction and building interactive systems that behave as expected. While we draw inspiration from cognitive sciences and symbolic AI, we aim to keep our concepts grounded in computer science for a wider audience.

Our mission extends beyond AI safety and performance; it's about shaping the world we want to live in. Even if programming becomes obsolete in 5 or 10 years, replaced by some magical prompt, we believe that traditional prompts are insufficient for preserving jobs. They're too simplistic and fail to accurately convey intentions.

In contrast, programming each reasoning step demands expert knowledge in prompt engineering and programming. Surprisingly, it's enjoyable and not that difficult for programmers, you'll gain insight into how AI truly operates by controlling it, beeing able to enhance the sequence of action and decision. Natural language combined with algorithms opens up endless possibilities. We can't envision a world without it.

## Support Our Work ❤️‍🔥

<a href="https://www.buymeacoffee.com/synalinks" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/default-orange.png" alt="Buy Me A Coffee" height="41" width="174"></a>

We're a small team dedicated to advancing the future of AI through open-source research. Consider supporting our work by contributing the cost of a coffee or by sharing this repository on social media! Your support helps us continue our research and development. Additionally, feel free to check out our progress, findings, and code on GitHub. We're grateful for any support and collaboration from the community as we work towards shaping the future of AI. Thank you!

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=SynaLinks/HybridAGI&type=Date)](https://star-history.com/#SynaLinks/HybridAGI&Date)