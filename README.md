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

## Quick Start (CLI version) 🚀

To start just use the following commands:
```
git clone https://github.com/SynaLinks/HybridAGI
cd HybridAGI
```

Rename `.env.template` to `.env` and replace `my-openai-api-key` with your actual API key, then, launch the app with:

```
docker-compose run --rm hybrid-agi-cli
```

To inspect the database, open your browser to [localhost:8001](https://localhost:8001) and connect to an existing database using `falkordb` hostname and port `6379`.

## Available Tools 🔨

You can use natively the following tools in your graph programs, and add more ones, if they are compatible with Langchain Tool format.

The AI system can interact with its long-term memory using the following tools:

- `WriteFiles`: Write into files, or override if existing
- `AppendFiles`: Append data to files, or create if non-existing
- `ReadFile`: Read data chunk by chunk (use multiple times to scroll)
- `Shell`: Enable basic unix commands: [`cd`, `ls`, `mkdir`, `mv`, `pwd`, `rm`]
- `Upload`: Archive and upload the target folder or file to the User
- `ContentSearch`: Perform a similarity based search on the filesystem and fetch the most relevant content

It can also perform several operations on its program memory:

- `ReadProgram`: Read a program based on its name
- `ProgramSearch`: Perform a similarity based search on the program memory and list the top-10 most relevant programs
- `LoadPrograms`: Load programs, override if existing (similar to `WriteFiles`)
- `CallProgram`: Call a program based on its name

Or on its working memory:

- `UpdateObjective`: Update the long-term objective of the agent
- `UpdateNote`: Update the note (used to learn from mistakes)
- `Predict`: Populate the prompt with intermediary data for reasoning
- `RevertTrace`: Remove from the trace the N last steps
- `ClearTrace`: Clear the trace from the prompt

The system can interact with the User using the following tools:

- `AskUser`: Ask a question to the User
- `Speak`: Tell something to the User

And fetch external data using:

- `InternetSearch`: Perform a DuckDuckGo search

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

```
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