# HybridAGI: The Programmable Neuro-Symbolic AGI
![Beta](https://img.shields.io/badge/Release-Beta-blue)
![CI](https://github.com/SynaLinks/HybridAGI/actions/workflows/python-package.yaml/badge.svg)
[![License: GPL-3.0](https://img.shields.io/badge/License-GPL-green.svg)](https://opensource.org/license/gpl-3-0/)
[![Documentation](https://img.shields.io/badge/Docs-Documentation-blue)](https://synalinks.github.io/documentation)
---

HybridAGI is the first *Programmable LLM-based Autonomous Agent* that lets you program its behavior using a **graph-based prompt programming** approach. This state-of-the-art feature allows the AGI to efficiently use any tool while controlling the long-term behavior of the agent.

## Key Features 🎉

- **Efficient Storage:** Thanks to an hybrid vector and graph database powered by FalkorDB enabling efficient storage of data you can inspect its long-term memory and known what's going on in a glance!

- **Graph-based Prompt Programming:** HybridAGI allows you to encode its behavior using programs represented as graphs. This capability, at the core of our approach, ensures that the system follows a structured and logical behavior. Want to adapt its behavior to your workflow? [Learn how to program HybridAGI using Cypher](https://synalinks.github.io/documentation)!

- **Graph Program Interpreter:** We introduce a [revolutionary Agent](hybridagi/interpreter/graph_program_interpreter.py) that leverages probabilistic decision making and graphs to determine actions based on a program. By reducing ambiguity and allowing composition of programs, this state-of-the-art feature enables the AGI to handle complex tasks with ease and precision.

- **Free Software:** HybridAGI is a community-driven project, fostering collaboration, innovation, and shared ownership. The software is released under the GNU GPL license, inviting contributions from a diverse range of users and empowering the collective intelligence of the community. Its architecture allows you to release your Cypher programs under *the license of your choice* while using the framework under GNU GPL.


## Quickstart in 5 simple steps!

#### What you need to start?
- An OpenAI API key or a functional text generation endpoint
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
┣ 📂archives  # This is where the AGI will save the archives when uploading file or folders
┣ 📂documentation # This is where you can put your pdf and documents for similarity search
┣ 📂programs # This is where you should put your Cypher programs
┣ 📂src # The source code of the UI
... the license and other files related to deployment
```

Note that these folders are shared with the application container, you should use them to share data between the user and the AI system.

### Echo test program

Start with a simple echo test, create a `main.cypher` file inside the `programs` folder:

```javascript
// Nodes declaration
CREATE
(start:Control {name:"Start"}),
(end:Control {name:"End"}),
(echo_objective:Action {
  name:"Reformulate the Objective",
  tool:"Speak",
  prompt:"Please reformulate the objective using other words"}),
// Structure declaration
(start)-[:NEXT]->(echo_objective),
(echo_objective)-[:NEXT]->(end)
```

Learn more about Graph-based Prompt Programming by reading our [documentation](https://synalinks.github.io/documentation/basics/graph-prompt-programming).

### Deploy your app

Now it is time to deploy this app, just use the following command

```shell
docker-compose up
```

### Inspect the database

Open your browser at `http://localhost:8001` and connect to an existing database with the hostname `falkordb` and port `6379`.

## Credits 👏

HybridAGI is made possible by the following open-source tools:

- [LangChain framework](https://www.langchain.com/)
- [FalkorDB database](https://www.falkordb.com/)

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

Join our community of developers, researchers, and AI enthusiasts. Contribute to the project, provide feedback, and shape the future of Hybrid AGI.