import dspy
from hybridagi import GraphProgramInterpreter
from hybridagi import SentenceTransformerEmbeddings
from hybridagi import ProgramMemory, AgentState
from pydantic import BaseModel
from dspy.teleprompt import BootstrapFewShot

print("Loading LLM & embeddings models...")
student_llm = dspy.OllamaLocal(model='mistral', max_tokens=1024, stop=["\n\n\n", "---"])
teacher_llm = dspy.OllamaLocal(model='mistral', max_tokens=1024, stop=["\n\n\n", "---"])

embeddings = SentenceTransformerEmbeddings(dim=384, model_name_or_path="sentence-transformers/all-MiniLM-L6-v2")

dspy.settings.configure(lm=student_llm)

model_path = "writer_agent.json"

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
    # If the agent is stuck in a loop we discard the example
    if pred.finish_reason == "max iters":
        return False
    with dspy.context(lm=teacher_llm):
        prediction = dspy.ChainOfThought(AssessAnswer)(
            assessed_answer = pred.final_answer,
            assessed_question = question,
        )
        result = dspy.TypedPredictor(CritiqueToScoreSignature)(critique=prediction.critique)
    return result.score.score

print("Initializing the program memory...")
program_memory = ProgramMemory(
    index_name = "qa_multi_hop",
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
(intro:Action {
    name: "Write the introduction for a news article on the objective's topic",
    tool: "Predict",
    prompt: "Imagine that you are a news writter, please give me an appealing introduction",
    output: "introduction"
}),
(first_paragraph:Action {
    name: "Write the first paragraph for a news article on the objective's topic",
    tool: "Predict",
    prompt: "Imagine that you are a news writter, please give me an appealing first paragraph, don't state that it is the first paragraph",
    output: "first_paragraph"
}),
(second_paragraph:Action {
    name: "Write the second paragraph for a news article on the objective's topic",
    tool: "Predict",
    prompt: "Imagine that you are a news writter, please give me an appealing second paragraph, don't state that it is the second paragraph",
    output: "second_paragraph"
}),
(third_paragraph:Action {
    name: "Write the third paragraph for a news article on the objective's topic",
    tool: "Predict",
    prompt: "Imagine that you are a news writter, please give me an appealing third paragraph, don't state that it is the third paragraph",
    output: "third_paragraph"
}),
(add_title_and_conclusion:Action {
    name: "Write the final version of the article, including a conclusion",
    tool: "Predict",
    prompt: "Your are a critique from a famous news paper
    Enhance this draft, Please ensure a coherent narrative:

    {introduction}

    {first_paragraph}

    {second_paragraph}

    {third_paragraph}",
    inputs = ["introduction", "first_paragraph", "second_paragraph", "third_paragraph"]
}),
(start)-[:NEXT]->(intro),
(intro)-[:NEXT]->(first_paragraph),
(first_paragraph)-[:NEXT]->(second_paragraph),
(second_paragraph)-[:NEXT]->(third_paragraph),
(third_paragraph)-[:NEXT]->(add_title_and_conclusion),
(add_title_and_conclusion)-[:NEXT]->(end)
""",
    ],
    ids = [
        "main",
    ]
)

dataset = [
    dspy.Example(objective="Write a news article about Climate Change").with_inputs("objective"),
    dspy.Example(objective="Write a news article about what are Low Techs").with_inputs("objective"),
]

testset = [
    dspy.Example(objective="Write a news article on Largue Language models").with_inputs("objective"),
]

print("Initializing the graph interpreter...")

agent_state = AgentState()

tools = []

interpreter = GraphProgramInterpreter(
    program_memory = program_memory,
    agent_state = agent_state,
    tools = tools,
)

print("Optimizing underlying prompts...")

config = dict(max_bootstrapped_demos=4, max_labeled_demos=0)

optimizer = BootstrapFewShot(
    teacher_settings=dict({'lm': teacher_llm}),
    metric = program_success,
    **config,
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
