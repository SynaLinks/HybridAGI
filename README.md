# Hybrid AGI: Unleash the Power of Combined Vector and Graph Databases
## The New AGI Operating System

HybridAGI is a **Programmable LLM Based Autonomous Agent**, build around 3 main concepts:
1. *The hybrid vector/graph database* which store both structured and unstructured data
2. *The meta knowledge graph* implementing a tailored filesystem for AI allowing the system to safely query information in a unix-like fashion
3. *The graph based prompt programming* allowing the system to follow logical and powerfull programs in the form of cypher files

![logo](img/synalinks_logo.png)

*Welcome to the HybridAGI repository, a cutting-edge, free, and open-source software that revolutionizes artificial general intelligence (AGI) systems. By combining the strengths of vector and graph databases, HybridAGI empowers users like you to collaborate with an intelligent system that goes beyond traditional AI capabilities.*



## ✨ Key Features

- **Efficient Storage:** HybridAGI's hybrid vector/graph database optimally stores both unstructured and structured knowledge acquired by the AGI system, ensuring efficient utilization of resources and maximizing performance.

- **Metagraph Representation:** The AGI system builds its own knowledge representation using a powerful [Metagraph](METAGRAPH.md), which acts as a dynamic map of its hybrid memory. This comprehensive snapshot allows for a holistic understanding of the system's knowledge landscape.

- **Graph-Based Prompt Programming:** HybridAGI allows you to encode its behavior using a Turing complete program represented as a Generalized Decision and Action Graph. This capability ensures that the system follows a structured and logical behavior. Want to adapt its behavior to your workflow? [Learn how to program HybridAGI](https://github.com/SynaLinks/HybridAGI-library)!

- **Graph Program Interpreter:** We introduce a [revolutionary agent](hybrid_agi/agents/interpreters/program_interpreter.py) that leverages logic and graphs to determine actions based on a program. By reducing ambiguity and employing probabilistic decision-making, this state-of-the-art feature enables the AGI to handle complex tasks with with precision, minimizing ambiguity.

- **Virtual Filesystem:** Leveraging the power of the metagraph, HybridAGI can seamlessly operate within its own memory, creating a virtual filesystem-like environment. This enables efficient data organization, retrieval, and manipulation, enhancing the system's ability to work with information effectively and safely.

- **Local Hybrid Storage:** HybridAGI prioritizes your data privacy and security. With local hybrid storage, you have complete ownership and control over your data, ensuring that sensitive information remains protected.

- **Free Software:** HybridAGI is a community-driven project, fostering collaboration, innovation, and shared ownership. The software is released under the GNU GPL license, inviting contributions from a diverse range of users and empowering the collective intelligence of the community.

## Roadmap

Thank you for checking out our project! Below is our exciting roadmap that outlines the future enhancements and features we plan to implement:

### Phase 1: Strengthening Core Functionality

In this phase, our primary focus will be on improving the core capabilities of the system to ensure a robust foundation for future developments.

- **Enhancing Self-Programming Capabilities**:
We are committed to pushing the boundaries of our system's self-programming capabilities. By leveraging HybridAGI graph programs, we aim to enable our system to imagine, develop and test its own graph programs. This means the system will become more efficient, adaptive, and capable of handling a broader range of tasks.

- **Enhancing Retrieval Capabilities**:
Efficient and accurate retrieval of information is essential. We'll work on optimizing our retrieval algorithms, speeding up the search process and providing users with more relevant results from the metagraph and hybridstore.

- **Developing a Fast Text-Only Language Model (LLM) with Large Context Size**:
In the context of HybridAGI, we recognize the significance of a dedicated language model tailored to text-based tasks. We will focus on creating an ultra-fast LLMs capable of processing vast amounts of text data efficiently. This LLM will be designed with extra-large context size, enabling HybridAGI to reason on longer programs and provide more accurate responses. We plan to train two different LLM, one for decision making and the other for acting allowing us to optimize speed and efficiency.

### Phase 2: Multimodal Support

Building on the strengthened core, we will focus on introducing multimodal support to the system, opening up exciting possibilities for diverse data types.

- **Adding Multimodal Support into the Metagraph and Hybridstore**:
We'll integrate support for various data modalities, including text, images, audio, and more. This enhancement will enable users to work with a rich array of data, enhancing the versatility and utility of the system.

- **Integrating External Tools for Multimodal Support**:
To ensure seamless handling and processing of different data modalities, we will collaborate with external tools and libraries specialized in multimodal data analysis. This integration will allow users to leverage cutting-edge technologies within our system.

We're constantly striving to improve and expand our project, and these roadmap milestones are just a glimpse of what's in store for the future. We highly value feedback and suggestions from our community, so if you have any ideas or feature requests, please feel free to open an issue or reach out to our team. Together, we'll create a powerful and versatile platform that meets the needs of various users and use cases. Stay tuned for more updates as we make progress on this exciting journey!

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