import dspy
from hybridagi import GraphProgramInterpreter
from hybridagi import SentenceTransformerEmbeddings
from hybridagi import ProgramMemory, TraceMemory
from hybridagi.tools import PredictTool, DuckDuckGoSearchTool
from pydantic import BaseModel
from dspy.teleprompt import BootstrapFewShot

print("Loading LLM & embeddings models...")
student_llm = dspy.OllamaLocal(model='mistral', max_tokens=1024, stop=["\n\n\n"])
teacher_llm = dspy.OllamaLocal(model='mistral', max_tokens=1024, stop=["\n\n\n"])

embeddings = SentenceTransformerEmbeddings(dim=384, model_name_or_path="sentence-transformers/all-MiniLM-L6-v2")

dspy.settings.configure(lm=student_llm)

model_path = "optional_websearch_qa.json"

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
    index_name = "optional_websearch_qa",
    embeddings = embeddings,
    wipe_on_start = True,
)

print("Initializing the trace memory...")
trace_memory = TraceMemory(
    index_name = "optional_websearch_qa",
    embeddings = embeddings,
)

print("Adding programs into memory...")
program_memory.add_texts(
    texts = [
"""
// @desc: The main program
CREATE
(start:Control {name:"Start"}),
(end:Control {name:"End"}),
(is_websearch_needed:Decision {
    name:"Check if searching for information online is needed to answer the objectve's question",
    question:"Is searching online needed to answer the objective's question?"
}),
(websearch:Action {
    name: "Perform a duckduckgo search",
    tool: "DuckDuckGoSearch",
    prompt: "Infer the search query to answer the given question"
}),
(answer:Action {
    name:"Answer the objective's question",
    tool:"Predict",
    prompt:"You are an helpfull assistant, answer the given question"
}),
(start)-[:NEXT]->(is_websearch_needed),
(is_websearch_needed)-[:YES]->(websearch),
(is_websearch_needed)-[:NO]->(answer),
(websearch)-[:NEXT]->(answer),
(answer)-[:NEXT]->(end)
""",
    ],
    ids = [
        "main",
    ]
)

dataset = [
    dspy.Example(objective="What is the capital of France?").with_inputs("objective"),
    dspy.Example(objective="Who is the current president of the United States?").with_inputs("objective"),
    dspy.Example(objective="What is the square root of 64?").with_inputs("objective"),
    dspy.Example(objective="What is the weather like in London today?").with_inputs("objective"),
    dspy.Example(objective="What is the chemical symbol for gold?").with_inputs("objective"),
    dspy.Example(objective="What is the latest news about space exploration?").with_inputs("objective"),
    dspy.Example(objective="What is the largest planet in our solar system?").with_inputs("objective"),
    dspy.Example(objective="Who won the Nobel Prize for Literature last year?").with_inputs("objective"),
    dspy.Example(objective="What is the value of pi up to two decimal places?").with_inputs("objective"),
    dspy.Example(objective="What is the current population of China?").with_inputs("objective"),
]

testset = [
    dspy.Example(objective="What is the tallest mountain in the world?").with_inputs("objective"),
    dspy.Example(objective="Who is the richest person in the world currently?").with_inputs("objective"),
    dspy.Example(objective="What is the formula for calculating the area of a circle?").with_inputs("objective"),
    dspy.Example(objective="What is the latest news about COVID-19 vaccines?").with_inputs("objective"),
    dspy.Example(objective="What is the chemical formula for water?").with_inputs("objective"),
]

tools = [
    PredictTool(),
    DuckDuckGoSearchTool(),
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

print("Evaluate baseline model")
baseline_score = evaluate(interpreter)
print("Evaluate optimized model")
eval_score = evaluate(compiled_interpreter)

print(f"Baseline: {baseline_score}")
print(f"Score: {eval_score}")

print(f"Save optimized model to '{model_path}'")
compiled_interpreter.save(model_path)
