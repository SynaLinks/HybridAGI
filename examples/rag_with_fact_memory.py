import dspy
from hybridagi import GraphProgramInterpreter
from hybridagi import SentenceTransformerEmbeddings
from hybridagi import ProgramMemory, FactMemory
from hybridagi.tools import EntityAddTool
from pydantic import BaseModel
from dspy.teleprompt import BootstrapFewShot

print("Loading LLM & embeddings models...")
student_llm = dspy.OllamaLocal(model='mistral', max_tokens=1024, stop=["\n\n\n"])
teacher_llm = dspy.OllamaLocal(model='mistral', max_tokens=1024, stop=["\n\n\n"])

embeddings = SentenceTransformerEmbeddings(dim=384, model_name_or_path="sentence-transformers/all-MiniLM-L6-v2")

dspy.settings.configure(lm=student_llm)

model_path = "rag_with_fact_memory.json"

class AssessAnswer(dspy.Signature):
    """Assess the success of the trace according to the objective"""
    assessed_answer = dspy.InputField(desc="The answer to assess")
    assessed_question = dspy.InputField(desc="The question to be assessed")
    critique = dspy.OutputField(desc="The critique of the answer")

class Score(BaseModel):
    score: float

class CritiqueToScoreSignature(dspy.Signature):
    """Convert a critique into a score between 0.0 and 1.0"""
    critique = dspy.InputField(desc="The critique to convert into a score")
    score: Score = dspy.OutputField(desc="A score between 0.0 and 1.0")

def program_success(example, pred, trace=None):
    question = example.objective
    with dspy.context(lm=teacher_llm):
        prediction = dspy.ChainOfThought(AssessAnswer)(
            assessed_answer = pred.final_answer,
            assessed_question = question,
        )
        result = dspy.TypedPredictor(CritiqueToScoreSignature)(critique=prediction.critique)
    return result.score.score

print("Initializing the program memory...")
program_memory = ProgramMemory(
    index_name = "rag_with_fact_memory",
    embeddings = embeddings,
    wipe_on_start = True,
)

print("Initializing the fact memory...")
fact_memory = FactMemory(
    index_name = "rag_with_fact_memory",
    embeddings = embeddings,
    wipe_on_start = True,
)

print("Adding Cypher programs into the program memory...")
program_memory.add_texts(
    texts = [
"""
// @desc: The main program
CREATE
(start:Control {name:"Start"}),
(end:Control {name:"End"}),
(entity_add:Action {
    name: "Create a fact memory entity based on the objective's question",
    tool: "EntityAdd",
    prompt: "Use the objective's question to infer triplets and add them to the fact memory"
}),
(start)-[:NEXT]->(entity_add),
(entity_add)-[:NEXT]->(end)
""",
    ],
    ids = [
        "main",
    ]
)

documents_texts = """
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

dataset = []
documents = documents_texts.split("\n\n")
train_size = int(0.8 * len(documents))
for i, document_text in enumerate(documents):
    if i < train_size:
        dataset.append(
            dspy.Example(objective=document_text).with_inputs("objective")
        )
    else:
        testset = [
            dspy.Example(objective=document_text).with_inputs("objective")
        ]

tools = [
    EntityAddTool(
        fact_memory = fact_memory,
        embeddings = embeddings,
    )
]

print("Optimizing underlying prompts...")
config = dict(max_bootstrapped_demos=4, max_labeled_demos=0)

optimizer = BootstrapFewShot(
    teacher_settings=dict({'lm': teacher_llm}),
    metric = program_success,
    **config,
)

interpreter = GraphProgramInterpreter(
    program_memory = program_memory,
    tools = tools,
)

compiled_interpreter = optimizer.compile(
    interpreter,
    trainset=dataset,
    valset=testset,
)

evaluate = dspy.evaluate.Evaluate(
    devset = testset,
    metric = program_success,
    num_threads = 1,
    display_progress = True,
    display_table = 0,
)

print("Evaluate baseline model")
try:
    baseline_score = evaluate(interpreter)
except Exception:
    baseline_score = 0.0
print("Evaluate optimized model")
try:
    eval_score = evaluate(compiled_interpreter)
except Exception:
    eval_score = 0.0

print(f"Baseline: {baseline_score}")
print(f"Score: {eval_score}")

print(f"Save optimized model to '{model_path}'")
compiled_interpreter.save(model_path)