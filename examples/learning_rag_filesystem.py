import dspy
from hybridagi import GraphProgramInterpreter
from hybridagi import SentenceTransformerEmbeddings
from hybridagi import ProgramMemory, FileSystem, TraceMemory, AgentState
from hybridagi.tools import (
    PredictTool,
    DocumentSearchTool,
    DuckDuckGoSearchTool,
    WriteFileTool,
)
from pydantic import BaseModel
from dspy.teleprompt import BootstrapFewShot

print("Loading LLM & embeddings models...")
student_llm = dspy.OllamaLocal(model='mistral', max_tokens=1024, stop=["\n\n\n"])
teacher_llm = dspy.OllamaLocal(model='mistral', max_tokens=1024, stop=["\n\n\n"])

embeddings = SentenceTransformerEmbeddings(dim=384, model_name_or_path="sentence-transformers/all-MiniLM-L6-v2")

dspy.settings.configure(lm=student_llm)

model_path = "learning_rag.json"

class AssessProgramSuccess(dspy.Signature):
    """Assess the success of the trace according to the objective"""
    assessed_trace = dspy.InputField(desc="The trace to assess")
    assessed_question = dspy.InputField(desc="The question to be assessed")
    critique = dspy.OutputField(desc="The critique of the trace")

class Score(BaseModel):
    score: float

class CritiqueToScoreSignature(dspy.Signature):
    """Convert a critique into a score between 0.0 and 1.0"""
    critique = dspy.InputField(desc="The critique to convert to a score")
    score: Score = dspy.OutputField(desc="A score between 0.0 and 1.0")

def program_success_metric(example, pred, trace=None):
    objective = example.objective
    sucessfull = f"How well does the program trace reflect the achievement of its intended objective: {objective}"
    with dspy.context(lm=teacher_llm):
        prediction = dspy.ChainOfThought(AssessProgramSuccess)(
            assessed_trace = pred.program_trace,
            assessed_question = sucessfull,
        )
        result = dspy.TypedPredictor(CritiqueToScoreSignature)(critique=prediction.critique)
    return result.score.score

print("Initializing the program memory...")
program_memory = ProgramMemory(
    index_name = "learning_rag",
    embeddings = embeddings,
    wipe_on_start = True,
)

print("Initializing the internal filesystem...")
filesystem = FileSystem(
    index_name = "learning_rag",
    embeddings = embeddings,
)

print("Initializing the trace memory...")
trace_memory = TraceMemory(
    index_name = "learning_rag",
    embeddings = embeddings,
)

print("Adding Cypher programs into the program memory...")
program_memory.add_texts(
    texts = [
"""
// @desc: The main program
CREATE
(start:Control {name:"Start"}),
(end:Control {name:"End"}),
(document_search:Action {
    name: "Search to documents to answer the objective's question",
    tool: "DocumentSearch",
    prompt: "Use the objective's question to infer the search query"
}),
(is_answer_known:Decision {
    name:"Check if the answer to the objective's question is in the above search",
    question: "Do you known the answer based on the above document search not based on prior knowledge?"
}),
(websearch:Action {
    name: "Perform a duckduckgo search",
    tool: "DuckDuckGoSearch",
    prompt: "Use the objective's question to infer the search query"
}),
(answer_web:Action {
    name: "Answer the objective's question based on the web search",
    tool: "Predict",
    prompt: "Use the above web search to infer the answer"
}),
(answer:Action {
    name: "Answer the objective's question based on the document search",
    tool: "Predict",
    prompt: "Use the above document search to infer the answer"
}),
(save_answer:Action {
    name: "Save the answer to the objective's question",
    tool: "WriteFile",
    prompt: "
Use the final answer to the objective's question to infer the content of the file,
Use the objective's question to infer its snake case filename
The content should be ONE paragraph only containing the answer.
Please always ensure to correctly infer the content of the file, don't be lazy."
}),
(start)-[:NEXT]->(document_search),
(document_search)-[:NEXT]->(is_answer_known),
(is_answer_known)-[:YES]->(answer),
(is_answer_known)-[:NO]->(websearch),
(websearch)-[:NEXT]->(answer_web),
(answer_web)-[:NEXT]->(save_answer),
(save_answer)-[:NEXT]->(end),
(answer)-[:NEXT]->(end)
""",
    ],
    ids = [
        "main",
    ]
)

dataset = [
    dspy.Example(objective="What is the definition of machine learning?").with_inputs("objective"),
    dspy.Example(objective="Who made significant contributions to the field of quantum computing?").with_inputs("objective"),
    dspy.Example(objective="Explain me what is a Large Language Model").with_inputs("objective"),
    dspy.Example(objective="What is a neuro-symbolic artificial intelligence?").with_inputs("objective"),
    dspy.Example(objective="When did the French Revolution occur?").with_inputs("objective"),
    dspy.Example(objective="Can you explain the theory of relativity?").with_inputs("objective"),
    dspy.Example(objective="Can you explain the concept of blockchain technology?").with_inputs("objective"),
    dspy.Example(objective="What ethical considerations should be taken into account regarding the integration of AI into various job sectors?").with_inputs("objective"),
    dspy.Example(objective="Can you explain Pythagoras theorem?").with_inputs("objective"),
    dspy.Example(objective="What is a blockchain?").with_inputs("objective"),
]

testset = [
    dspy.Example(objective="Can you explain the concept of blockchain technology?").with_inputs("objective"),
    dspy.Example(objective="Does the lasagna contains tomatoes?").with_inputs("objective"),
    dspy.Example(objective="When did the French Revolution occur?").with_inputs("objective"),
    dspy.Example(objective="What is a blockchain?").with_inputs("objective"),
    dspy.Example(objective="What is the recipe of lasagna?").with_inputs("objective"),
]

agent_state = AgentState()

tools = [
    PredictTool(),
    DocumentSearchTool(
        filesystem = filesystem,
        embeddings = embeddings,
    ),
    DuckDuckGoSearchTool(),
    WriteFileTool(
        filesystem = filesystem,
        agent_state = agent_state,
    )

]

print("Optimizing underlying prompts...")

config = dict(max_bootstrapped_demos=4, max_labeled_demos=4)

optimizer = BootstrapFewShot(
    teacher_settings=dict({'lm': teacher_llm}),
    metric = program_success_metric,
    **config,
)

interpreter = GraphProgramInterpreter(
    program_memory = program_memory,
    trace_memory = trace_memory,
    agent_state = agent_state,
    tools = tools,
)

compiled_interpreter = optimizer.compile(
    interpreter,
    trainset=dataset,
    valset=testset,
)

evaluate = dspy.evaluate.Evaluate(
    devset = testset,
    metric = program_success_metric,
    num_threads = 1,
    display_progress = True,
    display_table = 0,
)

filesystem.clear()
print("Evaluate baseline model")
baseline_score = evaluate(interpreter)

filesystem.clear()
print("Evaluate optimized model")
eval_score = evaluate(compiled_interpreter)

print(f"Baseline: {baseline_score}")
print(f"Score: {eval_score}")

print(f"Save optimized model to '{model_path}'")
compiled_interpreter.save(model_path)
