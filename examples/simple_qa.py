import dspy
from hybridagi import GraphProgramInterpreter
from hybridagi import SentenceTransformerEmbeddings
from hybridagi import ProgramMemory
from hybridagi.tools import PredictTool
from pydantic import BaseModel
from dspy.teleprompt import BootstrapFewShot

print("Loading LLM & embeddings models...")
student_llm = dspy.OllamaLocal(model='mistral', max_tokens=1024)
teacher_llm = dspy.OllamaLocal(model='mistral', max_tokens=1024)

embeddings = SentenceTransformerEmbeddings(dim=384, model_name_or_path="sentence-transformers/all-MiniLM-L6-v2")

dspy.settings.configure(lm=student_llm)

model_path = "simple_qa.json"

class Score(BaseModel):
    score: float

class AssessProgramSuccess(dspy.Signature):
    """Assess the success of the trace according to the objective"""
    assessed_trace = dspy.InputField(desc="The trace to assess")
    assessed_question = dspy.InputField(desc="The question to be assessed")
    score: Score = dspy.OutputField(desc="A score between 0.0 and 1.0 without additonal details")

def program_success_metric(example, pred, trace=None):
    objective = example.objective
    sucessfull = f"How well does the program trace reflect the achievement of its intended objective: {objective}?"
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
(answer:Action {
    name:"Answer the objective's question",
    tool:"Predict",
    prompt:"You are an helpfull assistant, answer the given question"
}),
(start)-[:NEXT]->(answer),
(answer)-[:NEXT]->(end)
""",
    ],
    ids = [
        "main",
    ]
)

dataset = [
    dspy.Example(objective="What is the city of the spacial and robotics industry in France?").with_inputs("objective"),
    dspy.Example(objective="What is a neuro-symbolic artificial intelligence?").with_inputs("objective"),
    dspy.Example(objective="What is prompt self-refinement?").with_inputs("objective"),
    dspy.Example(objective="How might advancements in artificial intelligence impact the future job market?").with_inputs("objective"),
    dspy.Example(objective="What ethical considerations should be taken into account regarding the integration of AI into various job sectors?").with_inputs("objective"),
    dspy.Example(objective="What are some potential societal implications of widespread automation driven by AI?").with_inputs("objective"),
    dspy.Example(objective="How might AI influence the skills and competencies that are in demand in the job market?").with_inputs("objective"),
    dspy.Example(objective="How can governments and policymakers ensure that the benefits of AI are distributed equitably across society, particularly in terms of employment opportunities?").with_inputs("objective"),
    dspy.Example(objective="What measures can be taken to ensure that AI technologies are used responsibly in the context of employment and recruitment?").with_inputs("objective"),
    dspy.Example(objective="How might AI assist in addressing challenges related to workplace diversity, equity, and inclusion?").with_inputs("objective"),
]

testset = [
    dspy.Example(objective="What are the risks and benefits associated with the use of AI in performance evaluation and decision-making processes within organizations?").with_inputs("objective"),
    dspy.Example(objective="What are the potential effects of AI on job mobility and geographical distribution of employment opportunities?").with_inputs("objective"),
    dspy.Example(objective="What are the negative implications of AI for the gig economy and freelance work?").with_inputs("objective"),
    dspy.Example(objective="What are some potential industries or professions that could be significantly affected by AI in the coming years? list 5 of them").with_inputs("objective"),
    dspy.Example(objective="How can individuals prepare themselves for a future where AI plays a more prominent role in the workforce?").with_inputs("objective"),
]

print("Initializing the graph interpreter...")

tools = [
    PredictTool(),
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
