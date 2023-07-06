# Hybrid AGI: Unleash the Power of Combined Vector and Graph Databases

[![](https://dcbadge.vercel.app/api/server/BX5wTy6H)](https://discord.gg/BX5wTy6H)

## The New AGI Operating System!

Welcome to the HybridAGI repository, a cutting-edge, free, and open-source software that revolutionizes artificial general intelligence (AGI) systems. By combining the strengths of vector and graph databases, HybridAGI empowers users like you to collaborate with an intelligent system that goes beyond traditional AI capabilities.

## ✨ Key Features

- **Efficient Storage:** HybridAGI's hybrid vector/graph database optimally stores both unstructured and structured knowledge acquired by the AGI system, ensuring efficient utilization of resources and maximizing performance.

- **Metagraph Representation:** The AGI system builds its own knowledge representation using a powerful [Metagraph](METAGRAPH.md), which acts as a dynamic map of its hybrid memory. This comprehensive snapshot allows for a holistic understanding of the system's knowledge landscape.

- **Hybrid Knowledge Retrieval:** HybridAGI empowers users with versatile knowledge retrieval capabilities. It can explicitly request textual and graph data from the system's memory using Cypher queries, enabling precise and targeted information retrieval. Additionally, the system supports similarity-based retrieval, allowing you to discover related knowledge based on semantic similarity. This flexible approach caters to diverse information needs and enhances the exploration of knowledge.

- **Granular Knowledge Exploration:** By aggregating graphs across different levels of abstraction, HybridAGI gains valuable insights. This granular approach enables a detailed understanding of the interconnectedness and relationships within the knowledge, facilitating advanced reasoning and analysis.

- **Graph-Based Programming:** HybridAGI allows you to encode its behavior using a Turing complete program represented as a Generalized Decision and Action Graph. This capability ensures that the system follows a structured and logical behavior. Want to adapt its behavior to your workflow? [Learn how to program HybridAGI](https://github.com/SynaLinks/HybridAGI-library)!

- **Graph Program Interpreter:** We introduce a revolutionary agent that leverages logic and graphs to determine actions based on a program. By reducing ambiguity and employing probabilistic decision-making, this state-of-the-art feature enables the AGI to handle complex tasks with ease and safety.

- **Virtual Filesystem:** Leveraging the power of the metagraph, HybridAGI can seamlessly operate within its own memory, creating a virtual filesystem-like environment. This enables efficient data organization, retrieval, and manipulation, enhancing the system's ability to work with information effectively and safely.

- **Local Hybrid Storage:** HybridAGI prioritizes your data privacy and security. With local hybrid storage, you have complete ownership and control over your data, ensuring that sensitive information remains protected.

- **Free Software:** HybridAGI is a community-driven project, fostering collaboration, innovation, and shared ownership. The software is released under the GNU GPL license, inviting contributions from a diverse range of users and empowering the collective intelligence of the community.

## 💡 Why Hybrid AGI Systems Matter

Hybrid AGI systems offer numerous advantages that propel the field of AGI forward:

- **Efficient Data Representation:** Graphs excel at representing complex data and offer flexibility in querying.
- **Enhanced Reasoning Capabilities:** The combination of structured and unstructured data reduces hallucination and enables reasoning on various data types.
- **Uncovering Complex Relationships:** By navigating paths in graphs, the AGI system can discover hidden and intricate connections between different concepts.
- **Integrating Prior Knowledge:** The system can leverage structured and unstructured prior knowledge such as business processes, ontologies, and documentation to enhance its understanding.
- **Structured Planning:** Graphs enable the AGI system to follow structured programs with precision, minimizing ambiguity.

## 🎉 Installation

To get started with HybridAGI, follow these steps:

1. Clone the repository to your local machine:
   ```
   git clone https://github.com/SynaLinks/HybridAGI
   ```

2. Install the required dependencies by running the following command:
   ```
   pip3 install -r requirements.txt
   ```

3. Install the programs library by executing the provided script:
   ```
   ./install_library.sh
   ```

   If you want to use the private mode, which uses a local model instead of OpenAI's models, run:
   ```
   ./install_local.sh
   ```

   For more information on setting up the local model, refer to the [LocalAI documentation](https://github.com/go-skynet/LocalAI).

4. Update the `.env.template` file with your details and preferences, and rename it to `.env`.

## 🗃️ Setting up the Hybrid Database

To set up the hybrid database, follow these steps:

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

1. Load the source code of HybridAGI if you wish to use it to upgrade itself:
   ```
   python3 load_source.py // Use the --clear option to reset the hybridstore
   ```

2. Load the programs into the database:
   ```
   python3 load_programs.py // Use the --clear option to reset the hybridstore
   ```

3. Once the database is set up, launch the AGI with the following command:
   ```
   chainlit run app.py -w
   ```

   For a command-line interface without GUI, you can launch the AGI with:
   ```
   python3 main.py
   ```

## Credits

Hybrid AGI is made possible by the following open-source tools:

- LangChain framework
- Redis software stack
- OpenAI API
- LocalAI
- ChainLit

## Get Involved

Join our community of developers, researchers, and AI enthusiasts. Contribute to the project, provide feedback, and shape the future of Hybrid AGI. Together, let's unlock the true potential of combined vector and graph databases in the realm of Artificial General Intelligence!