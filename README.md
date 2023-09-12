# Hybrid AGI: Unleash the Power of Neuro-Symbolic AGI
[![License: GPL-3.0](https://img.shields.io/badge/License-GPL-green.svg)](https://opensource.org/license/gpl-3-0/)

*Welcome to HybridAGI repository, a cutting-edge, free, and open-source software that revolutionizes artificial general intelligence (AGI) systems. By combining the strengths of large language models (LLM) and symbolic artificial intelligence, HybridAGI empowers users like you to collaborate with an intelligent system that goes beyond traditional AI capabilities.*

HybridAGI is a **Programmable LLM Based Autonomous Agent**, build around 3 main concepts:
1. *The hybrid vector/graph database* used as knowledge base, filesystem and program memory
2. *The meta knowledge graph* implementing a tailored filesystem for AI allowing the system to safely query information in a unix-like fashion
3. *The graph based prompt programming* allowing the system to follow logical and powerfull programs in the form of cypher files

## ✨ Key Features

- **Efficient Storage:** [SymboLinks](https://github.com/SynaLinks/SymboLinks) is an hybrid vector and graph database used as knowledge base, filesystem and program memory. This database enables the AGI system to work safely within its own memory in a unix-like fashion.

- **Graph-Based Prompt Programming:** HybridAGI allows you to encode its behavior using programs represented as graphs. This capability, at the core of our approach, ensures that the system follows a structured and logical behavior. Want to adapt its behavior to your workflow? [Learn how to program HybridAGI](https://github.com/SynaLinks/HybridAGI-library)!

- **Graph Program Interpreter:** We introduce a [revolutionary agent](hybrid_agi/interpreter/graph_program_interpreter.py) that leverages probabilistic decision making and graphs to determine actions based on a program. By reducing ambiguity, this state-of-the-art feature enables the AGI to handle complex tasks with ease and precision.

- **Free Software:** HybridAGI is a community-driven project, fostering collaboration, innovation, and shared ownership. The software is released under the GNU GPL license, inviting contributions from a diverse range of users and empowering the collective intelligence of the community.

## 🎉 Quick Start

To start just use the following commands:
```
git clone https://github.com/SynaLinks/HybridAGI
cd HybridAGI
docker-compose run --rm hybrid-agi
```

To inspect the hybridstore, open your browser to [localhost:8001](https://localhost:8001) and connect to your database using `redis` hostname and port `6379`.

## Credits

Hybrid AGI is made possible by the following open-source tools:

- LangChain framework
- Redis software stack
- OpenAI API
- LocalAI

## Get Involved

Join our community of developers, researchers, and AI enthusiasts. Contribute to the project, provide feedback, and shape the future of Hybrid AGI. Together, let's unlock the true potential of combined vector and graph databases in the realm of Artificial General Intelligence!