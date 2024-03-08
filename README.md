# HybridAGI: The Programmable Neuro-Symbolic AGI for people who want AI to behave as expected
![Beta](https://img.shields.io/badge/Release-Beta-blue)
![Coverage](coverage.svg)
![CI](https://github.com/SynaLinks/HybridAGI/actions/workflows/python-package.yaml/badge.svg)
[![License: GPL-3.0](https://img.shields.io/badge/License-GPL-green.svg)](https://opensource.org/license/gpl-3-0/)
[![Documentation](https://img.shields.io/badge/Docs-Documentation-blue)](https://synalinks.github.io/documentation)
---

HybridAGI is the *first Programmable LLM-based Autonomous Agent* that lets you program its behavior using a **graph-based prompt programming** approach. This state-of-the-art feature allows the AGI to efficiently use any tool while controlling the long-term behavior of the agent.

Become the *first Prompt Programmers in history*; be a part of the AI revolution one node at a time!

## Key Features 🎉

- **For AI makers:** This framework is intended for data scientists, prompt engineers, researchers, and AI enthusiasts who love to experiment with AI. This product requires some programming and prompt engineering knowledge to get the best out of it. It's a Build Yourself product where the focus is on human creativity rather than AI autonomy. If you are new to prompt engineering, start by looking at [this guide](https://www.promptingguide.ai/).

- **Memory-Centric AGI:** Thanks to a hybrid vector and graph database powered by [FalkorDB](https://www.falkordb.com/) enabling efficient storage of data, you can inspect its long-term memory and know what's going on at a glance! The AGI remembers its programs, can execute, or modify them dynamically.

- **Graph-based Prompt Programming:** HybridAGI allows you to encode its behavior using programs represented as graphs. This capability, at the core of our approach, ensures that the system follows a structured and logical behavior enabling conditional loops and multi-output decisions. Want to adapt its behavior to your workflow? [Learn how to program HybridAGI](https://synalinks.github.io/documentation/basics/graph-prompt-programming) using [Cypher](https://en.wikipedia.org/wiki/Cypher_(query_language))!

- **Graph Program Interpreter:** We introduce a revolutionary [LLM Agent as Graph Interpreter](hybridagi/interpreter/graph_program_interpreter.py) that leverages probabilistic decision-making and graphs to determine actions based on a program. By reducing ambiguity and allowing composition of programs, this state-of-the-art feature enables the AGI to handle complex tasks with ease and precision.

- **One Prompt At a Time:** Our interpreter focuses on the current node's prompt to predict tool input, eliminating role confusion. This allows for seamless integration of multiple role-based prompts in the same program, enhancing flexibility, adaptability, and performance.

- **Use Open-Source Models:** HybridAGI's symbolic system offloads planning capabilities, enabling the use of smaller open-source LLM models. This results in a cost-effective, faster, and more sustainable solution. Guide the reasoning process of your agents efficiently and create better ones with fewer resources.

- **Free Software:** HybridAGI is a community-driven project, fostering collaboration, innovation, and shared ownership. The software is released under the GNU GPL license, inviting contributions from a diverse range of users and empowering the collective intelligence of the community. Its architecture allows you to *release your Cypher programs under the **license of your choice*** while using the framework under GNU GPL.

- **Do it Yourself:** The drawback to offloading the Agent planning capabilities to the symbolic components means that you have to build the algorithm yourself. Sure, you can emulate a React/MKRL Agent with a conditional loop and a decision... but where is the fun in that? You can find better, more specific to your use case, and more performant!

Many people think prompt engineering is an already dead discipline. The truth is that it's just the beginning of the journey; we have only scratched the surface of what is possible. Our product, HybridAGI, opens up new possibilities by making it possible to build entire conversational applications using prompt programs only, so you can focus on what matters:

*✨Finding the best prompt algorithm to fit your use case and quickly create AI that **behave as expected**✨*

## Chat Demo: Quickstart in 5 simple steps !

#### What you need to start?

- A MistralAI API key (get one at https://mistral.ai/)
- [Git](https://git-scm.com/downloads) and [Docker](https://www.docker.com/products/docker-desktop/)

### Installation

First, clone the chat repository with:

```shell
git clone https://github.com/SynaLinks/HybridAGI-chat
cd HybridAGI-chat
```

### Directory hierarchy

Then you should open the repository folder in your favorite IDE ([VSCodium](https://vscodium.com/) with the Neo4J plugin is a good start). 

```shell
📦HybridAGI-chat
┣ 📂archives  # This is where the AGI will save its uploaded work
┣ 📂documentation # This is where you can put your pdf and documents
┣ 📂programs # This is where you should put your Cypher programs
┣ 📂src # The source code of the UI
... the license and other files related to deployment
```

Note that the folders `archives`, `documentation` and `programs` are shared with the application container, you can edit them and reload your programs/documentation without restarting the application container.

### Echo test program

Start with a simple echo test, create a `main.cypher` file inside the `programs` folder:

main.cypher:
```javascript
// Nodes declaration
CREATE
(start:Control {name:"Start"}),
(end:Control {name:"End"}),
(echo_objective:Action {
    name:"Reformulate the Objective",
    tool:"Speak",
    prompt:"Please reformulate the objective using other words"
}),
// Structure declaration
(start)-[:NEXT]->(echo_objective),
(echo_objective)-[:NEXT]->(end)
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
(refine_objective)-[:NEXT]->(is_anything_unclear)
// The outgoing edges of decision nodes give
// the possible answers to the system
(is_anything_unclear)-[:YES]->(ask_question),
(is_anything_unclear)-[:NO]->(end),
// Decisions can have multiple arbitrary outcomes
(is_anything_unclear)-[:MAYBE]->(ask_question)
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
(echo_objective:Action {
    name:"Reformulate the Objective",
    tool:"Speak",
    prompt:"Please reformulate the objective using other words"
}),
// Structure declaration
(start)-[:NEXT]->(clarify_objective),
(clarify_objective)-[:NEXT]->(echo_objective),
(echo_objective)-[:NEXT]->(end)
```

Learn more about Graph-based Prompt Programming by reading our [documentation](https://synalinks.github.io/documentation/basics/graph-prompt-programming).

Then explore the curated [list of Cypher primitives](https://github.com/SynaLinks/primitives-pack) to speed up your development.

### Deploy your chat app

Now it is time to deploy this app, just use the following command

```shell
docker-compose up
```

## CLI Demo (use asyncio to speed-up inference)

To use the CLI demo, rename the `.env.template` file into `.env`, replace `your-api-key` with your actual MistralAI API key and use the following command:

```
docker compose run -it hybrid-agi-cli
```

### Inspect the database

Open your browser at `http://localhost:8001` and connect to an existing database with the hostname `hybrid-agi-db` and port `6379`.

## Available Tools 🛠️

| Tool         | Description                               |
|--------------|:------------------------------------------:|
| `WriteFiles` | Write into files, or override if existing |
| `AppendFiles`|  Append data to files, or create if non-existing |
| `ReadFile` | Read data chunk by chunk (use multiple times to scroll) |
| `Shell` | Replicate unix commands to navigate inside the hybrid database: [`cd`, `ls`, `mkdir`, `mv`, `pwd`, `rm`, `tree`] |
| `RemoteShell` | Allow remote command execution inside a sandbox container |
| `Upload` | Archive and upload the target folder or file to the User |
| `ContentSearch` | Perform a similarity based search and fetch the content |
| `ReadProgram` | Read a program based on its name |
| `ProgramSearch` | Perform a similarity based search and list the top-5 most relevant |
| `LoadPrograms` | Load programs, override if existing |
| `CallProgram` | Call a program based on its name |
| `UpdateObjective` | Update the long-term objective |
| `UpdateNote` | Update the note (used as reminder) |
| `Predict` | Populate the prompt with intermediary data for reasoning |
| `RevertTrace` | Remove from the trace the N last steps |
| `ClearTrace` | Clear the trace from the prompt |
| `AskUser` | Ask a question to the user |
| `Speak` | Tell something to the User |
| `InternetSearch` | Perform a DuckDuckGo search |
| `BrowseWebsite` | Browse a website chunk by chunk (use multiple times to scroll) |
| `Arxiv` | Perform a search on [Arxiv](https://arxiv.org/) |

## Credits 👏

HybridAGI is made possible by the following open-source tools:

- [LangChain](https://www.langchain.com/) framework
- [FalkorDB](https://www.falkordb.com/) database
- [MistralAI](https://mistral.ai) models

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