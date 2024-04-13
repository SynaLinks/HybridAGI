import dspy
from hybridagi import GraphProgramInterpreter
from hybridagi import SentenceTransformerEmbeddings
from hybridagi import ProgramMemory, TraceMemory, FileSystem, AgentState
from hybridagi.tools import (
    ProgramSearchTool,
    DocumentSearchTool,
    CallProgramTool,
    PredictTool,
    InternalShellTool,
    WriteFileTool,
    AppendFileTool,
    ReadFileTool,
    SpeakTool,
    AskUserTool,
    UpdateObjectiveTool,
)
from pydantic import BaseModel
from dspy.teleprompt import BootstrapFewShot

print("Loading LLM & embeddings models...")
student_llm = dspy.OllamaLocal(model='mistral', max_tokens=1024, stop=["\n\n\n"])
teacher_llm = dspy.OllamaLocal(model='mistral', max_tokens=1024, stop=["\n\n\n"])

embeddings = SentenceTransformerEmbeddings(dim=384, model_name_or_path="sentence-transformers/all-MiniLM-L6-v2")

dspy.settings.configure(lm=student_llm)

model_path = "dynamic_call_agent.json"

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
    index_name = "dynamic_call_agent",
    embeddings = embeddings,
    wipe_on_start = True,
)

program_memory.add_folders(["examples/primitives"])

print("Initializing the trace memory...")
trace_memory = TraceMemory(
    index_name = "dynamic_call_agent",
    embeddings = embeddings,
    wipe_on_start = True,
)

print("Initializing the filesystem...")
filesystem = FileSystem(
    index_name = "dynamic_call_agent",
    embeddings = embeddings,
    wipe_on_start = True,
)

print("Adding programs into memory...")
program_memory.add_texts(
    texts = [
"""
// @desc: Try to call an existing program
CREATE
(start:Control {name:"Start"}),
(end:Control {name:"End"}),
(program_search:Action {
    name:"Search for existing routine to fulfill the objective and list the top-5 most relevant", 
    tool:"ProgramSearch",
    prompt:"Use the objective to describe in ONE short sentence the action to take"
}),
(call_program:Action {
    name:"Pick the most appropriate routine from the previous search", 
    tool:"CallProgram",
    prompt:"Use the context to known which program to pick. Only infer the name of the program without addtionnal details."
}),
(start)-[:NEXT]->(program_search),
(program_search)-[:NEXT]->(call_program),
(call_program)-[:NEXT]->(end)
""",
    ],
    ids = [
        "main",
    ]
)

dataset = [
    dspy.Example(objective="Create a folder called Test").with_inputs("objective"),
    dspy.Example(objective="Write a poem about AI and nature into a file called poem.txt").with_inputs("objective"),
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

agent_state = AgentState()

tools = [
    PredictTool(),
    ProgramSearchTool(
        program_memory = program_memory,
        embeddings = embeddings,
    ),
    DocumentSearchTool(
        filesystem = filesystem,
        embeddings = embeddings,
    ),
    CallProgramTool(
        program_memory = program_memory,
        agent_state = agent_state,
    ),
    InternalShellTool(
        filesystem = filesystem,
        agent_state = agent_state,
    ),
    WriteFileTool(
        filesystem = filesystem,
        agent_state = agent_state,
    ),
    AppendFileTool(
        filesystem = filesystem,
        agent_state = agent_state,
    ),
    ReadFileTool(
        filesystem = filesystem,
        agent_state = agent_state,
    ),
    SpeakTool(
        agent_state = agent_state,
    ),
    AskUserTool(
        agent_state = agent_state,
    ),
]

print("Optimizing underlying prompts...")

config = dict(max_bootstrapped_demos=4, max_labeled_demos=4)

optimizer = BootstrapFewShot(
    teacher_settings=dict({'lm': teacher_llm}),
    metric = program_success,
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