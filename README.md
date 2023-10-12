# HybridAGI: The Programmable Neuro-Symbolic AGI
![Alpha](https://img.shields.io/badge/Release-Alpha-orange)
![CI](https://github.com/SynaLinks/HybridAGI/actions/workflows/python-package.yaml/badge.svg)
[![License: GPL-3.0](https://img.shields.io/badge/License-GPL-green.svg)](https://opensource.org/license/gpl-3-0/)

<center>
<img src="hybrid-chimera.png" alt="A cute hybrid chimera" width="300"> 
</center>

## We've released our Streamlit App! [Check this out!](https://github.com/SynaLinks/HybridAGI-app)



HybridAGI represents the future of hybrid architectures that combine the strengths of both machine learning models and explicit programming. This approach aims to bridge the gap between the impressive language generation abilities of Large Language Models (LLM) and the need for logical reasoning and decision-making capabilities. By integrating advanced machine learning models with explicit programming, HybridAGI systems excel in language generation, logical reasoning, and decision-making tasks.

HybridAGI is the first *Programmable LLM-based Autonomous Agent* that lets you program its behavior using a **graph-based prompt programming** approach. This state-of-the-art feature allows the AGI to efficiently use any tool while controlling the long-term behavior of the agent.

## ✨ Key Features

- **Efficient Storage:** Thanks to an hybrid vector and graph filesystem database enabling efficient storage of data the AI system can work safely within its own memory in a unix-like fashion.

- **Graph-based Prompt Programming:** HybridAGI allows you to encode its behavior using programs represented as graphs. This capability, at the core of our approach, ensures that the system follows a structured and logical behavior. Want to adapt its behavior to your workflow? [Learn how to program HybridAGI](https://github.com/SynaLinks/HybridAGI-library)!

- **Graph Program Interpreter:** We introduce a [revolutionary agent](hybrid_agi/interpreter/graph_program_interpreter.py) that leverages probabilistic decision making and graphs to determine actions based on a program. By reducing ambiguity, this state-of-the-art feature enables the AGI to handle complex tasks with ease and precision.

- **Free Software:** HybridAGI is a community-driven project, fostering collaboration, innovation, and shared ownership. The software is released under the GNU GPL license, inviting contributions from a diverse range of users and empowering the collective intelligence of the community. Its architecture allows you to release your programs under *the license of your choice* while using the framework under GNU GPL.

## 🎉 Quick Start

To start just use the following commands:
```
git clone https://github.com/SynaLinks/HybridAGI
cd HybridAGI
docker-compose run --rm hybrid-agi-cli
```

To inspect the database, open your browser to [localhost:8001](https://localhost:8001) and connect to an existing database using `falkordb` hostname and port `6379`.

## Tools

The AI system can interact with its long-term memory using the following tools:

- `WriteFiles`: Write into files, or override if existing
- `AppendFiles`: Append data to files, or create if non-existing
- `ReadFile`: Read data chunk by chunk (use multiple times to scroll)
- `Shell`: Enable basic unix commands: [`cd`, `ls`, `mkdir`, `mv`, `pwd`, `rm`]
- `Upload`: Archive and upload the target folder or file to the User
- `ContentSearch`: Perform a similarity based search on the filesystem

It can also perform several operations on its program memory:

- `ListPrograms`: List the programs based on similarity search
- `ProgramSearch`: Perform a similarity based search on the program memory
- `LoadPrograms`: Load programs, override if existing
- `CallProgram`: Call a program based on its name

Or on its working memory:

- `UpdateObjective`: Update the long-term objective of the agent
- `Predict`: Populate the prompt with intermediary data for reasoning
- `Revert`: Remove from the prompt the N last steps

The system can interact with the User using the following tools:

- `AskUser`: Ask a question to the User
- `Speak`: Tell something to the User

And fetch external data using:

- `InternetSearch`: Perform a DuckDuckGo search

## Credits

HybridAGI is made possible by the following open-source tools:

- [LangChain framework](https://www.langchain.com/)
- [FalkorDB database](https://www.falkordb.com/)

## Get Involved

Join our community of developers, researchers, and AI enthusiasts. Contribute to the project, provide feedback, and shape the future of Hybrid AGI.