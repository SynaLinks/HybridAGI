# FAQ

## Frequently Asked Questions

### Why HybridAGI?

We are dissatisfied with the current trajectory of agent-based systems that lack control and efficiency. Today's approach involves building React/MKRL agents that operate independently without human control, often leading to infinite loops of nonsense due to their tendency to stay within their data distribution. Multi-agent systems attempt to address this issue, but they often result in more nonsense and prohibitive costs due to the agents' chitchat. Additionally, today's agents often require fine-tuning to enhance or correct their behavior, which can be a time-consuming and complex process.

With HybridAGI, the only thing you need to do is modify the behavior graph (the graph programs). We believe that fine-tuning should be a last resort when in-context learning fails to yield the desired results. By rooting cognitive sciences into computer science concepts, we empower programmers to build the agent system of their dreams by controlling the sequence of action and decision. Our goal is to build an agent system that can solve real-world problems by using an intermediary language that is interpretable by both humans and machines. If we want to keep humans in the loop in the coming years, we need to design agent systems for that purpose.

### What is the difference between LangGraph and HybridAGI?

LangGraph is built on top of LangChain, which was also the case for HybridAGI last year. However, given the direction of the LangChain team towards encouraging ReACT agents that lack control and explainability, we switched to DSPy, which provides better value by focusing on pipelines optimization. Recently, LangGraph has emerged to compensate for the poor decision-making of LangChain, but we had already proven the value of our work. Moreover, LangGraph, like many agentic frameworks, describes a static finite state machine. Our vision of AGI systems is that being Turing complete is required, which is the case for many agentic frameworks, but having the capability of programming itself on the fly (meaning real continuous learning) is also required to truly begin the AGI journey, which is lacking in other frameworks.

### What is the difference between Llama-Index and HybridAGI?

Llama-Index recently released an event-driven agent system, similar to LangGraph, it is a static state machine, and the same remarks apply to their work.

### What is the difference between DSPy and HybridAGI?

HybridAGI is built on top of the excellent work of the DSPy team, and it is intended as an abstraction to simplify the creation of complex DSPy programs in the context of LLM Agents. DSPy is more general and is also used for simpler tasks that don't need agentic systems. Unlike DSPy, our programs are not static but dynamic and can adapt to the user query by dynamically calling programs stored in memory. Moreover, we focus our work on explainable neuro-symbolic AGI systems using Graphs. The graph programs are easier to build than implementing them from scratch using DSPy. If DSPy is the PyTorch of LLM applications, think of HybridAGI as the Keras or HuggingFace of neuro-symbolic LLM agents.

### What is the difference between OpenAI o1 and HybridAGI?

OpenAI o1 and HybridAGI share many common goals, but they are built with different paradigms in mind. Like OpenAI o1, HybridAGI uses multi-step inferences and is a goal-oriented agent system. However, unlike OpenAI o1, we guide the CoT trace of our agent system instead of letting it explore freely its action space, a paradigm more similar to an A* where the Agent navigates in a defined graph instead of a Q-learning one. This results in more efficient reasoning, as experts can program it to solve a particular use case. We can use smaller LLMs, reducing the environmental impact and increasing the ROI. The downside of our technology is that you need expert knowledge in your domain as well as in programming and AI systems to best exploit its capabilities. For that reason, we provide audit, consulting, and development services to people and companies that lack the technical skills in AI to implement their system.

### Who are we?

We're not based in Silicon Valley or part of a big company; we're a small, dedicated team from the south of France. Our focus is on delivering an AI product where the user maintains control. We're dissatisfied with the current trajectory of agent-based products. We are experts in human-robot interactions and building interactive systems that behave as expected. While we draw inspiration from cognitive sciences and symbolic AI, we aim to keep our concepts grounded in computer science for a wider audience.

Our mission extends beyond AI safety and performance; it's about shaping the world we want to live in. Even if programming becomes obsolete in 5 or 10 years, replaced by some magical prompt, we believe that traditional prompts are insufficient for preserving jobs. They're too simplistic and fail to accurately convey intentions.

In contrast, programming each reasoning step demands expert knowledge in prompt engineering and programming. Surprisingly, it's enjoyable and not that difficult for programmers, as it allows you to gain insight into how AI truly operates by controlling it. Natural language combined with algorithms opens up endless possibilities. We can't envision a world without it.

### How do we make money?

We are providing audit, consulting, and development services for businesses that want to implement neuro-symbolic AI solutions in various domains, from computer vision to high-level reasoning with knowledge graph/ontology systems in critical domains like health, biology, financial, aerospace, and many more.

HybridAGI is a research project to showcase our capabilities but also to bring our vision of safe AGI systems for the future. We are a bootstrapped start-up that seeks real-world use cases instead of making pretentious claims to please VCs and fuel the hype.

Because our vision of LLMs capabilities is more moderate than others, we are actively looking to combine different fields of AI (evolutionary, symbolic, and deep learning) to make this leap into the future without burning the planet by relying on scaling alone. Besides the obvious environmental impacts, by relying on small/medium models, we have a better understanding and the capability to make useful research without trillion-worth datacenters.

HybridAGI is our way to be prepared for that future and at the same time, showcase our understanding of modern and traditional AI systems. HybridAGI is the proof that you don't need billion of dollars to work on AGI systems, and that a small team of passionate people can make the difference.

### Why did we release our work under GNU GPL?

We released HybridAGI under GNU GPL for various reasons, the first being that we want to protect our work and the work of our contributors. The second reason is that we want to build a future for people to live in, without being dependent on Big AI tech companies, we want to empower people not enslave them by destroying the market and leaving people jobless without a way to become proprietary of their knowledge. HybridAGI is a community project, by the community, for the community. Finally, HybridAGI is a way to connect with talented and like-minded people all around the world and create a community around a desirable future.

### Is HybridAGI just a toolbox?

Some could argue that HybridAGI is just a toolbox. However, unlike LangChain or Llama-Index, HybridAGI has been designed from the ground up to work in synergy with a special-purpose LLM trained on our DSL/architecture. We have enhanced our software thanks to the community and because we are the ones who created our own programming language, we are also the best people to program it. We have accumulated data and learned many augmentation techniques and cleaned our datasets during the last year of the project to keep our competitive advantage. We might release the LLM we are building at some point in time when we decide that it is beneficial for us to do so.

### Can I use HybridAGI commercially?

Our software is released under GNU GPL license to protect ourselves and the contributions of the community. The logic of your application being separated (the graph programs) there is no IP problem for you to use HybridAGI. Moreover, when used in production, you surely want to make a FastAPI server to request your agent and separate the backend and frontend of your app (like a website), so the GPL license doesn't contaminate the other pieces of your software. We also provide dual-licensing for our clients if needed.