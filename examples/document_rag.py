import dspy
from hybridagi import GraphProgramInterpreter
from hybridagi import SentenceTransformerEmbeddings
from hybridagi import ProgramMemory, FileSystem
from hybridagi.tools import PredictTool, DocumentSearchTool
from pydantic import BaseModel
from dspy.teleprompt import BootstrapFewShot

documents_ids = [
    "/home/user/synalinks_presentation.txt",
]

documents_texts = [
"""
SynaLinks is a young French start-up founded in Toulouse in 2023.
Our mission is to promote a responsible and pragmatic approach to general artificial intelligence.
To achieve this, we integrate deep learning models with symbolic artificial intelligence models, the traditional domain of AI before the era of deep learning.

At SynaLinks, our approach aims to combine the efficiency of deep learning models with the transparency and explicability of symbolic models, thus creating more robust and ethical artificial intelligence systems. 
We work on cutting-edge technologies that enable businesses to fully harness the potential of AI while retaining significant control over their systems, reducing the risks associated with opacity and dependence on deep learning algorithms.

We work closely with our clients to customize our solutions to meet their specific needs.
Our neuro-symbolic approach offers the flexibility necessary to address the diverse requirements of businesses, allowing them to remain masters of their AI.

We are confident that AI can be a positive force for society and the economy,rather than a source of concern.
We are committed to playing an active role in promoting responsible AI use while contributing to the advancement of the fourth industrial revolution.

As a start-up based in Toulouse, we take pride in being part of the French technological ecosystem and contributing to innovation in the field of AI.
Our future is centered on ongoing research, improving our products and services, and creating a world where AI is a driver of progress, ethics, and profitability for businesses.
"""
]

print("Loading LLM & embeddings models...")
student_llm = dspy.OllamaLocal(model='mistral', max_tokens=1024, stop=["\n\n"])
teacher_llm = dspy.OllamaLocal(model='mistral', max_tokens=1024, stop=["\n\n"])

embeddings = SentenceTransformerEmbeddings(dim=384, model_name_or_path="sentence-transformers/all-MiniLM-L6-v2")

dspy.settings.configure(lm=student_llm)

model_path = "document_rag.json"


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
    index_name = "document_rag",
    embeddings = embeddings,
    wipe_on_start = True,
)

print("Initializing the internal filesystem...")
filesystem = FileSystem(
    index_name = "document_rag",
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
    name: "Search to information to answer the objective's question",
    tool: "DocumentSearch",
    prompt: "Use the objective's question to infer the search query"
}),
(answer:Action {
    name: "Answer the objective's question",
    tool: "Predict",
    prompt: "You are an helpfull assistant, answer the given question using the above search"
}),
(start)-[:NEXT]->(document_search),
(document_search)-[:NEXT]->(answer),
(answer)-[:NEXT]->(end)
""",
    ],
    ids = [
        "main",
    ]
)

print("Adding documents to the filesystem...")

filesystem.add_texts(
    texts = documents_texts,
    ids = documents_ids,
)

dataset = [
    dspy.Example(objective="What is the primary mission of SynaLinks as a start-up?").with_inputs("objective"),
    dspy.Example(objective="How does SynaLinks approach the development of artificial intelligence systems?").with_inputs("objective"),
    dspy.Example(objective="What technologies does SynaLinks work on to enable businesses to fully utilize AI?").with_inputs("objective"),
    dspy.Example(objective="How does SynaLinks ensure transparency and explicability in their AI models?").with_inputs("objective"),
    dspy.Example(objective="What role do deep learning models play in SynaLinks approach to AI?").with_inputs("objective"),
    dspy.Example(objective="How does SynaLinks help businesses reduce risks associated with AI opacity and dependence?").with_inputs("objective"),
    dspy.Example(objective="How does SynaLinks customize their solutions to meet client's specific needs?").with_inputs("objective"),
    dspy.Example(objective="What is the neuro-symbolic approach offered by SynaLinks?").with_inputs("objective"),
    dspy.Example(objective="How does SynaLinks aim to contribute to the advancement of the fourth industrial revolution?").with_inputs("objective"),
    dspy.Example(objective="What is SynaLinks stance on the role of AI in society and the economy?").with_inputs("objective"),
]

testset = [
    dspy.Example(objective="How does SynaLinks promote responsible AI use?").with_inputs("objective"),
    dspy.Example(objective="As a French start-up, how does SynaLinks contribute to the local technological ecosystem?").with_inputs("objective"),
    dspy.Example(objective="What are SynaLinks future plans in terms of research and development?").with_inputs("objective"),
    dspy.Example(objective="How does SynaLinks envision AI as a driver of progress, ethics, and profitability?").with_inputs("objective"),
    dspy.Example(objective="How does SynaLinks ensure that businesses remain in control of their AI systems?").with_inputs("objective"),
]

tools = [
    PredictTool(),
    DocumentSearchTool(
        index_name = "document_rag",
        embeddings = embeddings,
    ),
]

print("Optimizing underlying prompts...")

config = dict(max_bootstrapped_demos=4, max_labeled_demos=4)

optimizer = BootstrapFewShot(
    teacher_settings=dict({'lm': teacher_llm}),
    metric = program_success_metric,
    **config,
)

interpreter = GraphProgramInterpreter(program_memory = program_memory, tools = tools)

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

print("Evaluate baseline model")
baseline_score = evaluate(interpreter)
print("Evaluate optimized model")
eval_score = evaluate(compiled_interpreter)

print(f"Baseline: {baseline_score}")
print(f"Score: {eval_score}")

print(f"Save optimized model to '{model_path}'")
compiled_interpreter.save(model_path)
