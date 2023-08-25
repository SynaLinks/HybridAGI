# Hybrid AGI
## The Safe and Programmable Neuro-Symbolic AGI

HybridAGI is a **Programmable LLM Based Autonomous Agent**, build around 3 main concepts:
1. *The hybrid vector/graph database* which store both structured and unstructured data
2. *The meta knowledge graph* implementing a tailored filesystem for AI allowing the system to safely query information in a unix-like fashion
3. *The graph based prompt programming* allowing the system to follow logical and powerfull programs in the form of cypher files

![logo](img/synalinks_logo.png)

*Welcome to the HybridAGI repository, a cutting-edge, free, and open-source software that revolutionizes artificial general intelligence (AGI) systems. By combining the strengths of vector and graph databases, HybridAGI empowers users like you to collaborate with an intelligent system that goes beyond traditional AI capabilities.*

## ✨ Key Features

- **Efficient Storage:** HybridAGI's hybrid vector and graph database [SymboLinks](https://github.com/SynaLinks/SymboLinks) optimally stores both unstructured and structured knowledge acquired by the AGI system, ensuring efficient utilization of resources and maximizing performance. This enables the AGI system to work within its own memory in a unix-like fashion.

- **Graph-Based Prompt Programming:** HybridAGI allows you to encode its behavior using a Turing complete program represented as a Decision and Action Graph. This capability ensures that the system follows a structured and logical behavior. Want to adapt its behavior to your workflow? [Learn how to program HybridAGI](https://github.com/SynaLinks/HybridAGI-library)!

- **Graph Program Interpreter:** We introduce a [revolutionary agent](hybrid_agi/agents/grapĥ_program_interpreter.py) that leverages logic and graphs to determine actions based on a program. By reducing ambiguity and employing probabilistic decision-making, this state-of-the-art feature enables the AGI to handle complex tasks with with precision, minimizing ambiguity.

- **Free Software:** HybridAGI is a community-driven project, fostering collaboration, innovation, and shared ownership. The software is released under the GNU GPL license, inviting contributions from a diverse range of users and empowering the collective intelligence of the community.

## 🎉 Installation

To get started with HybridAGI, follow these steps:

1. Clone the repository to your local machine:
   ```
   git clone https://github.com/SynaLinks/HybridAGI
   cd HybridAGI
   ```

2. Install the required dependencies by running the following command:
   ```
   pip3 install -r requirements.txt
   ```

3. Install SymboLinks, the hybrid vector and graph database using this script:
   ```
   ./install_symbolinks.sh
   ```

4. Install the programs library by executing the provided script:
   ```
   ./install_library.sh
   ```

5. If you want to use the private mode, which uses a local model instead of OpenAI's models, run:
   ```
   ./install_local.sh
   ```

   For more information on setting up the local model, refer to the [LocalAI documentation](https://github.com/go-skynet/LocalAI).

6. Update the `.env.template` file with your details and preferences, and rename it to `.env`.

## 🗃️ Setting up the Database

To set up the database, follow these steps:

1. Launch Redis by executing the following command:
   ```
   docker run -p 6379:6379 -it --rm redis/redis-stack-server:latest
   ```

2. Launch RedisInsight by executing the following command:
   ```
   docker run -v redisinsight:/db -p 8001:8001 redislabs/redisinsight:latest
   ```

3. Open your browser and navigate to [http://localhost:8001](http://localhost:8001).

4. In RedisInsight, use the IP address of your Docker container and the port number `6379` to connect to the Redis server.

## 🚀 Launch Hybrid AGI

To launch HybridAGI, follow these steps:

1. Load the source code of HybridAGI (optional only if you wish to use it to upgrade itself):
   ```
   python3 load_source.py // Use the --clear option to reset the hybridstore
   ```

2. Load the programs into the database (mandatory):
   ```
   python3 load_programs.py // Use the --clear option to reset the hybridstore
   ```

3. Once the database is set up, you can launch the AGI with:
   ```
   python3 main.py
   ```

## Credits

Hybrid AGI is made possible by the following open-source tools:

- LangChain framework
- Redis software stack
- OpenAI API
- LocalAI

## Get Involved

Join our community of developers, researchers, and AI enthusiasts. Contribute to the project, provide feedback, and shape the future of Hybrid AGI. Together, let's unlock the true potential of combined vector and graph databases in the realm of Artificial General Intelligence!