import dspy
from hybridagi import GraphProgramInterpreter
from hybridagi import SentenceTransformerEmbeddings
from hybridagi import ProgramMemory
from hybridagi.tools import PredictTool, DuckDuckGoSearchTool
from pydantic import BaseModel
from dspy.teleprompt import BootstrapFewShot

print("Loading LLM & embeddings models...")
student_llm = dspy.OllamaLocal(model='mistral', max_tokens=1024, stop=["\n\n"])
teacher_llm = dspy.OllamaLocal(model='mistral', max_tokens=1024, stop=["\n\n"])

embeddings = SentenceTransformerEmbeddings(dim=384, model_name_or_path="sentence-transformers/all-MiniLM-L6-v2")

dspy.settings.configure(lm=student_llm)

model_path = "optional_websearch_qa.json"

class Score(BaseModel):
    score: float

class AssessProgramSuccess(dspy.Signature):
    """Assess the success of the trace according to the objective"""
    assessed_trace = dspy.InputField(desc="The trace to assess")
    assessed_question = dspy.InputField(desc="The question to be assessed")
    score: Score = dspy.OutputField(desc="A score between 0.0 and 1.0 without additional details")

def program_success_metric(example, pred, trace=None):
    objective = example.objective
    sucessfull = f"How well does the program trace reflect the achievement of its intended objective: {objective}"
    with dspy.context(lm=teacher_llm):
        result = dspy.TypedPredictor(AssessProgramSuccess)(
            assessed_trace = pred.program_trace,
            assessed_question = sucessfull,
        )
    return result.score.score

print("Initializing the program memory...")
program_memory = ProgramMemory(
    index_name = "simple_qa",
    embeddings = embeddings,
    wipe_on_start = True,
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
    name:"Check if searching for information online is needed to answer",
    question:"Is searching online needed?"
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

compiled_prompt_opt = optimizer.compile(
    GraphProgramInterpreter(program_memory = program_memory, tools = tools),
    trainset=dataset,
    valset=testset,
)

print("Evaluate optimized model")

evaluate = dspy.evaluate.Evaluate(
    devset = testset, 
    metric = program_success_metric,
    num_threads = 1,
    display_progress = True,
    display_table = 0,
)

eval_score = evaluate(compiled_prompt_opt)

print(f"Score: {eval_score}")

print(f"Save optimized model to '{model_path}'")
compiled_prompt_opt.save(model_path)
