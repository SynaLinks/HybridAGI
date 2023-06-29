# Hybrid AGI: Unleash the Power of Combined Vector and Graph Databases
## The New AGI Operating System. Alpha release !

*Hybrid AGI is a cutting-edge, free, and open-source software that revolutionizes artificial general intelligence (AGI) systems. By combining the strengths of vector and graph databases, it empowers users like you to collaborate with an intelligent system that goes beyond traditional AI capabilities.*

## ✨ Key Features

- **Efficient Storage:** The hybrid vector/graph database optimally stores both unstructured and structured knowledge acquired by the AGI system, ensuring efficient utilization of resources and maximizing performance. 

- **Metagraph Representation:** The AGI system builds its own knowledge representation using a powerful [Metagraph](METAGRAPH.md), which acts as a dynamic map of its hybrid memory. This comprehensive snapshot allows for a holistic understanding of the system's knowledge landscape.

- **Hybrid knowledge retrieval:** The AGI system empowers users with versatile knowledge retrieval capabilities. It can explicitly request textual and graph data from the system's memory using Cypher queries, enabling precise and targeted information retrieval. Additionally, the system supports similarity-based retrieval, allowing you to discover related knowledge based on semantic similarity. This flexible approach caters to diverse information needs and enhances the exploration of knowledge.

- **Granular knowledge exploration:** By aggregating graphs across different levels of abstraction, the AGI system gains valuable insights. This granular approach enables a detailed understanding of the interconnectedness and relationships within the knowledge, facilitating advanced reasoning and analysis.

- **Graph Based Programming:** The AGI system encode its behavior using a turing complete program represented as an action and decision graph. This capability ensure the system to follow a structured and logical behavior. Wants to adapt its behavior to your workflow? [Learn how to program Hybrid AGI](PROGRAMS.md)!

- **Graph Program Interpreter:** We introduce a revolutionary Agent that leverages logic and graphs to determine actions based on a program. By reducing ambiguity and employing probabilistic decision this state-of-the-art feature enables the AGI to handle complex tasks with ease and safety.

- **Virtual Filesystem:** Leveraging the power of the metagraph, the AGI system can seamlessly operate within its own memory, creating a virtual filesystem-like environment. This enables efficient data organization, retrieval, and manipulation, enhancing the system's ability to work with information effectively and safely.

- **Local Hybrid Storage:** Hybrid AGI prioritizes your data privacy and security. With local hybrid storage, you have complete ownership and control over your data, ensuring that sensitive information remains protected.

- **Free Software:** Hybrid AGI is a community-driven project, fostering collaboration, innovation, and shared ownership. The software is under GNU GPL, inviting contributions from a diverse range of users, and empowering the collective intelligence of the community.

## 💡 Why Hybrid AGI Systems Matter

Hybrid AGI systems offer numerous advantages that propel the field of AGI forward:

- **Efficient data representation:** Graphs excel at representing complex data and offer flexibility in querying.
- **Enhanced reasoning capabilities:** The combination of structured and unstructured data reduces hallucination and enables reasoning on various data types.
- **Uncovering complex relationships:** By navigating paths in graphs, the AGI system can discover hidden and intricate connections between different concepts.
- **Integrating prior knowledge:** The system can leverage structured and unstructured prior knowledge such as business processes, ontologies, and documentation to enhance its understanding.
- **Structured planning:** Graphs enable the AGI system to follow structured plans with precision, minimizing ambiguity.

## Install

```
git clone https://github.com/SynaLinks/HybridAGI
pip3 install -r requirements.txt
```

Install the programs library:
```
./install_library.sh
```

If you want to use the private mode (uses a local model instead of OpenAI's models):
```
./install_local.sh
```
More information on how to setup for local model [here](https://github.com/go-skynet/LocalAI)

## Setup

Update the `.env.template` with your details and preferences and rename it `.env`

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

3. Open your browser at [http://localhost:8001](http://localhost:8001).

4. In RedisInsight, use the IP address of your Docker container and the port number indicated as `6379` here.

## 🚀 Launch Hybrid AGI

First, you need to load the source code of HybridAGI if you wish to use it to upgrade itself:
```
python3 load_source.py --clear // Use the clear option to reset the hybridstore
```

Then, load the programs into the database:
```
python3 load_programs.py --clear // Use the clear option to reset the hybridstore
```

Once the database is set up, launch the AGI with the following command:
```
chainlit run app.py -w
```

For the bolds, you can launch the AGI without GUI with:
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

Join our community of developers, researchers, and AI enthusiasts. Contribute to the project, provide feedback, and shape the future of Hybrid AGI.
